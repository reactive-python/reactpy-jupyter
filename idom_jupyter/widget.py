import asyncio
from functools import wraps
from threading import Thread

import ipywidgets as widgets
from IPython.display import display as ipython_display

from traitlets import Unicode, Instance
from idom.core.layout import Layout, LayoutEvent
from idom.core.dispatcher import SingleViewDispatcher

# See js/lib/widget.js for the frontend counterpart to this file.


def display(constructor, *args, **kwargs):
    """Function for converting IDOM elements to widgets and then displaying them"""
    return ipython_display(LayoutWidget(constructor, *args, **kwargs))


def widgetize(constructor):
    """A decorator that turns an IDOM element into a Jupyter Widget constructor"""

    @wraps(constructor)
    def wrapper(*args, **kwargs):
        return LayoutWidget(constructor, *args, **kwargs)

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

    def __init__(self, constructor, *args, **kwargs):
        super().__init__()
        self._func_args_kwargs = (constructor, args, kwargs)
        self.on_msg(self._idom_on_msg)
        self._idom_recv_queues = {}
        self._idom_loops = {}
        self.msgs = []

    @staticmethod
    def _idom_on_msg(self, message, buffers):
        self.msgs.append(message)
        m_type = message.get("type")
        if m_type == "client-ready":
            _spawn_async_daemon(self._idom_run_view(message["viewID"]))
        elif m_type == "dom-event":
            view_id = message["viewID"]
            queue = self._idom_recv_queues[view_id]
            event = LayoutEvent(**message["data"])
            self._idom_loops[view_id].call_soon_threadsafe(queue.put_nowait, event)

    async def _idom_run_view(self, view_id):
        self._idom_loops[view_id] = asyncio.get_event_loop()
        self._idom_recv_queues[view_id] = asyncio.Queue()

        async def send(data):
            self.send({"viewID": view_id, "data": data})

        async def recv():
            self.msgs.append(["recv", view_id])
            return await self._idom_recv_queues[view_id].get()

        f, a, kw = self._func_args_kwargs
        async with SingleViewDispatcher(Layout(f(*a, **kw))) as dispatcher:
            await dispatcher.run(send, recv, None)


def _spawn_async_daemon(coro):
    def run_in_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)

    thread = Thread(target=run_in_thread, daemon=True)
    thread.start()

    return thread
