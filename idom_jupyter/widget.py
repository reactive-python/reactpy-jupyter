import asyncio
from urllib.parse import urljoin
from functools import wraps
from threading import Thread
from queue import Queue as SyncQueue

import ipywidgets as widgets
from IPython import get_ipython
from IPython.display import display as ipython_display
from notebook import notebookapp
from traitlets import Unicode, Instance
from idom.core.layout import Layout, LayoutEvent, LayoutUpdate
from idom.client.protocol import ClientImplementation, client_implementation

# See js/lib/widget.js for the frontend counterpart to this file.


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
    _view_module_version = Unicode("^0.1.0").tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode("^0.1.0").tag(sync=True)

    _client_ready_callbacks = Instance(widgets.CallbackDispatcher, ())

    def __init__(self, element):
        super().__init__()
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


_NOTEBOOK_BASE_URL = None


def _get_base_url_of_current_notebook():
    global _NOTEBOOK_BASE_URL
    if _NOTEBOOK_BASE_URL is None:
        ipython_home_dir = get_ipython().home_dir
        for server_info in notebookapp.list_running_servers():
            if ipython_home_dir == server_info["notebook_dir"]:
                _NOTEBOOK_BASE_URL = server_info["base_url"]
                break
        else:
            raise ValueError(
                f"Could not find a notebook running in {ipython_home_dir!r}"
            )
    return _NOTEBOOK_BASE_URL


class _IdomJupyterClient(ClientImplementation):
    """An implementation of IDOM's client interface for Jupyter"""

    web_module_exports = staticmethod(client_implementation.current.web_module_exports)
    web_module_exists = staticmethod(client_implementation.current.web_module_exists)
    web_module_names = staticmethod(client_implementation.current.web_module_names)
    web_module_path = staticmethod(client_implementation.current.web_module_path)
    add_web_module = staticmethod(client_implementation.current.add_web_module)

    @staticmethod
    def web_module_url(name):
        # see idom_jupyter.jupyter_server_extension for info on this
        return urljoin(
            _get_base_url_of_current_notebook(), f"_idom_web_modules/{name}.js"
        )


client_implementation.current = _IdomJupyterClient()
