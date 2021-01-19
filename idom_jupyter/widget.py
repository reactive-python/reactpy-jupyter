import asyncio
from functools import wraps
from threading import Thread
from queue import Queue as SyncQueue

import ipywidgets as widgets
from IPython.display import display as ipython_display
from traitlets import Unicode
from idom.core.layout import Layout, LayoutEvent, LayoutUpdate


_JUPYTER_SERVER_BASE_URL = ""


def set_jupyter_server_base_url(base_url):
    global _JUPYTER_SERVER_BASE_URL
    _JUPYTER_SERVER_BASE_URL = base_url


def run(constructor):
    """Run the given IDOM elemen definition as a Jupyter Widget.

    This function is meant to be similarly to ``idom.run``.
    """
    return ipython_display(LayoutWidget(constructor()))


def widgetize(constructor):
    """A decorator that turns an IDOM element into a Jupyter Widget constructor"""

    @wraps(constructor)
    def wrapper(*args, **kwargs):
        return LayoutWidget(constructor(*args, **kwargs))

    return wrapper


@widgets.register
class LayoutWidget(widgets.DOMWidget):
    """A widget for displaying IDOM elements"""

    # Name of the widget view class in front-end
    _view_name = Unicode("IdomView").tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode("IdomModel").tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode("idom-client-jupyter").tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode("idom-client-jupyter").tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode("^0.4.0").tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode("^0.4.0").tag(sync=True)

    _jupyter_server_base_url = Unicode().tag(sync=True)

    def __init__(self, element):
        super().__init__(_jupyter_server_base_url=_JUPYTER_SERVER_BASE_URL)
        self._idom_model = {}
        self._idom_views = set()
        self._idom_layout = Layout(element)
        self._idom_loop = _spawn_threaded_event_loop(self._idom_layout_render_loop())
        self.on_msg(self._idom_on_msg)

    @staticmethod
    def _idom_on_msg(self, message, buffers):
        m_type = message.get("type")
        if m_type == "client-ready":
            v_id = message["viewID"]
            self._idom_views.add(v_id)
            update = LayoutUpdate.create_from({}, self._idom_model)
            self.send({"viewID": v_id, "data": update})
        elif m_type == "dom-event":
            asyncio.run_coroutine_threadsafe(
                self._idom_layout.dispatch(LayoutEvent(**message["data"])),
                loop=self._idom_loop,
            )
        elif m_type == "client-removed":
            v_id = message["viewID"]
            if v_id in self._idom_views:
                self._idom_views.remove(message["viewID"])

    async def _idom_layout_render_loop(self):
        async with self._idom_layout:
            while True:
                update = await self._idom_layout.render()

                self._idom_model = update.apply_to(self._idom_model)
                for v_id in self._idom_views:
                    self.send({"viewID": v_id, "data": update})


def _spawn_threaded_event_loop(coro):
    loop_q = SyncQueue()

    def run_in_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop_q.put(loop)
        loop.run_until_complete(coro)

    thread = Thread(target=run_in_thread, daemon=True)
    thread.start()

    return loop_q.get()
