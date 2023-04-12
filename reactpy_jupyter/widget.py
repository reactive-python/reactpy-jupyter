from __future__ import annotations

import asyncio
from functools import wraps
from pathlib import Path
from threading import Thread
from queue import Queue as SyncQueue
from typing import Any, Awaitable, Callable

from typing_extensions import ParamSpec

import anywidget
from jsonpointer import set_pointer
import ipywidgets as widgets
from IPython.display import display as ipython_display, DisplayHandle
from traitlets import Unicode
from reactpy.core.layout import Layout
from reactpy.config import REACTPY_DEBUG_MODE
from reactpy.core.types import ComponentType, LayoutUpdateMessage

if REACTPY_DEBUG_MODE.current:
    # from `npx vite`
    ESM = "http://localhost:5173/src/index.js?anywidget"
else:
    # from `npx vite build`
    bundled_assets_dir = Path(__file__).parent / "static"
    ESM = (bundled_assets_dir / "index.js").read_text()


def set_import_source_base_url(base_url: str) -> None:
    """Fallback URL for import sources, if no Jupyter Server is discovered by the client"""
    global _IMPORT_SOURCE_BASE_URL
    _IMPORT_SOURCE_BASE_URL = base_url


def run(constructor: Callable[[], ComponentType]) -> DisplayHandle | None:
    """Run the given ReactPy elemen definition as a Jupyter Widget.

    This function is meant to be similarly to ``reactpy.run``.
    """
    return ipython_display(LayoutWidget(constructor()))


_P = ParamSpec("_P")


def widgetize(constructor: Callable[_P, ComponentType]) -> Callable[_P, LayoutWidget]:
    """A decorator that turns an ReactPy element into a Jupyter Widget constructor"""

    @wraps(constructor)
    def wrapper(*args: Any, **kwargs: Any) -> LayoutWidget:
        return LayoutWidget(constructor(*args, **kwargs))

    return wrapper


class LayoutWidget(anywidget.AnyWidget):
    """A widget for displaying ReactPy elements"""

    _esm = ESM
    _import_source_base_url = Unicode().tag(sync=True)

    def __init__(self, component: ComponentType) -> None:
        super().__init__(_import_source_base_url=_IMPORT_SOURCE_BASE_URL)
        self._reactpy_model = {}
        self._reactpy_views = set()
        self._reactpy_layout = Layout(component)
        self._reactpy_loop = _spawn_threaded_event_loop(
            self._reactpy_layout_render_loop()
        )
        self.on_msg(lambda _, *args, **kwargs: self._reactpy_on_msg(*args, **kwargs))

    def _reactpy_on_msg(self, message: dict[str, Any], buffers: Any):
        m_type = message.get("type")
        if m_type == "client-ready":
            v_id = message["viewID"]
            self._reactpy_views.add(v_id)
            update_message = {
                "type": "layout-update",
                "path": "",
                "model": self._reactpy_model,
            }
            self.send({"viewID": v_id, "data": update_message})
        elif m_type == "dom-event":
            asyncio.run_coroutine_threadsafe(
                self._reactpy_layout.deliver(message["data"]),
                loop=self._reactpy_loop,
            )
        elif m_type == "client-removed":
            v_id = message["viewID"]
            if v_id in self._reactpy_views:
                self._reactpy_views.remove(message["viewID"])

    async def _reactpy_layout_render_loop(self) -> None:
        async with self._reactpy_layout:
            while True:
                update_message = await self._reactpy_layout.render()
                if not update_message["path"]:
                    self._reactpy_model = update_message["model"]
                else:
                    set_pointer(
                        self._reactpy_model,
                        update_message["path"],
                        update_message["model"],
                    )
                for v_id in self._reactpy_views:
                    self.send({"viewID": v_id, "data": update_message})

    def __repr__(self) -> str:
        return f"LayoutWidget({self._reactpy_layout})"


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