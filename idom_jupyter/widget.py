import asyncio
from threading import Thread

import ipywidgets as widgets
from traitlets import Unicode, Instance
from idom.core.layout import Layout as IdomLayout, LayoutEvent as IdomLayoutEvent
from idom.core.dispatcher import SingleStateDispatcher

# See js/lib/widget.js for the frontend counterpart to this file.


@widgets.register
class Layout(widgets.DOMWidget):
    """An example widget."""

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
        self._started = False
        self._loop = None

    @staticmethod
    def _idom_on_msg(self, message, buffers):
        m_type = message.get("type")
        if m_type == "client-ready" and not self._started:
            self._started = True
            _spawn_async_daemon(self._idom_run)
        elif m_type == "dom-event":
            event = IdomLayoutEvent(**message["data"])
            self._loop.call_soon_threadsafe(self._recv_queue.put_nowait, event)

    async def _idom_run(self):
        self._loop = asyncio.get_event_loop()
        self._recv_queue = asyncio.Queue()

        constructor, args, kwargs = self._func_args_kwargs
        root_element = constructor(*args, **kwargs)
        async with SingleStateDispatcher(IdomLayout(root_element)) as dispatcher:
            await dispatcher.run(self._idom_send, self._recv_queue.get, None)

    async def _idom_send(self, data):
        self.send(data)


def _spawn_async_daemon(coro):
    def run_in_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro())

    thread = Thread(target=run_in_thread, daemon=True)
    thread.start()

    return thread
