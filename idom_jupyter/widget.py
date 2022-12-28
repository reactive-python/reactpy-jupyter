from __future__ import annotations

import asyncio
from functools import wraps
from threading import Thread
from queue import Queue as SyncQueue
from typing import Any, Awaitable, Callable

from typing_extensions import ParamSpec

import ipywidgets as widgets
from IPython.display import display as ipython_display, DisplayHandle
from traitlets import Unicode
from idom.core.layout import Layout, LayoutEvent, LayoutUpdate
from idom.core.serve import VdomJsonPatch, render_json_patch
from idom.core.types import ComponentType

_IMPORT_SOURCE_BASE_URL = ""


def set_import_source_base_url(base_url: str) -> None:
    """Fallback URL for import sources, if no Jupyter Server is discovered by the client"""
    global _IMPORT_SOURCE_BASE_URL
    _IMPORT_SOURCE_BASE_URL = base_url


def run(constructor: Callable[[], ComponentType]) -> DisplayHandle | None:
    """Run the given IDOM elemen definition as a Jupyter Widget.

    This function is meant to be similarly to ``idom.run``.
    """
    return ipython_display(LayoutWidget(constructor()))


_P = ParamSpec("_P")


def widgetize(constructor: Callable[_P, ComponentType]) -> Callable[_P, LayoutWidget]:
    """A decorator that turns an IDOM element into a Jupyter Widget constructor"""

    @wraps(constructor)
    def wrapper(*args: Any, **kwargs: Any) -> LayoutWidget:
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
    _view_module_version = Unicode("^0.9.1").tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode("^0.9.1").tag(sync=True)

    _import_source_base_url = Unicode().tag(sync=True)

    def __init__(self, component: ComponentType) -> None:
        super().__init__(_import_source_base_url=_IMPORT_SOURCE_BASE_URL)
        self._idom_model = {}
        self._idom_views = set()
        self._idom_layout = Layout(component)
        self._idom_loop = _spawn_threaded_event_loop(self._idom_layout_render_loop())
        self.on_msg(lambda _, *args, **kwargs: self._idom_on_msg(*args, **kwargs))

    def _idom_on_msg(self, message: dict[str, Any], buffers: Any):
        m_type = message.get("type")
        if m_type == "client-ready":
            v_id = message["viewID"]
            self._idom_views.add(v_id)
            update = LayoutUpdate("", None, self._idom_model)
            diff = VdomJsonPatch.create_from(update)
            self.send({"viewID": v_id, "data": diff})
        elif m_type == "dom-event":
            asyncio.run_coroutine_threadsafe(
                self._idom_layout.deliver(LayoutEvent(**message["data"])),
                loop=self._idom_loop,
            )
        elif m_type == "client-removed":
            v_id = message["viewID"]
            if v_id in self._idom_views:
                self._idom_views.remove(message["viewID"])

    async def _idom_layout_render_loop(self) -> None:
        async with self._idom_layout:
            while True:
                diff = await render_json_patch(self._idom_layout)
                self._idom_model = diff.apply_to(self._idom_model)
                for v_id in self._idom_views:
                    self.send({"viewID": v_id, "data": diff})

    def __repr__(self) -> str:
        return f"LayoutWidget({self._idom_layout})"


def _spawn_threaded_event_loop(
    coro: Callable[..., Awaitable[Any]]
) -> asyncio.AbstractEventLoop:
    loop_q: SyncQueue[asyncio.AbstractEventLoop] = SyncQueue()

    def run_in_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop_q.put(loop)
        loop.run_until_complete(coro)

    thread = Thread(target=run_in_thread, daemon=True)
    thread.start()

    return loop_q.get()
