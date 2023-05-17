from __future__ import annotations

import asyncio
import os
from functools import wraps
from pathlib import Path
from queue import Queue as SyncQueue
from threading import Thread
from typing import Any, Awaitable, Callable, overload

import anywidget
from IPython.display import DisplayHandle
from IPython.display import display as ipython_display
from jsonpointer import set_pointer
from reactpy.core.layout import Layout
from reactpy.core.types import ComponentType
from ipywidgets import Widget, widget_serialization
from traitlets import Unicode, List, Instance
from typing_extensions import ParamSpec

from reactpy_jupyter.widget_component import InnerWidgets, inner_widgets_context

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


@overload
def to_widget(value: Callable[_P, ComponentType]) -> Callable[_P, LayoutWidget]:
    ...


@overload
def to_widget(value: ComponentType) -> LayoutWidget:
    ...


def to_widget(
    value: Callable[_P, ComponentType] | ComponentType
) -> Callable[_P, LayoutWidget] | LayoutWidget:
    """Turn a component into a widget or a component construtor into a widget constructor"""

    if isinstance(value, ComponentType):
        return LayoutWidget(value)

    @wraps(value)
    def wrapper(*args: Any, **kwargs: Any) -> LayoutWidget:
        return LayoutWidget(value(*args, **kwargs))

    return wrapper


class LayoutWidget(anywidget.AnyWidget):
    """A widget for displaying ReactPy elements"""

    _esm = ESM
    _import_source_base_url = Unicode().tag(sync=True)
    _inner_widgets = List(Instance(Widget)).tag(sync=True, **widget_serialization)

    def __init__(self, component: ComponentType) -> None:
        super().__init__(
            _import_source_base_url=_IMPORT_SOURCE_BASE_URL,
            _inner_widgets=[],
        )
        self._reactpy_model = {}
        self._reactpy_views = set()
        self._reactpy_layout = Layout(
            inner_widgets_context(
                component,
                value=InnerWidgets(self._add_inner_widget, self._remove_inner_widget),
            )
        )
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

    def _add_inner_widget(self, widget: Widget) -> None:
        self._inner_widgets = self._inner_widgets + [widget]

    def _remove_inner_widget(self, widget: Widget) -> None:
        self._inner_widgets = [w for w in self._inner_widgets if w != widget]

    def __repr__(self) -> str:
        return f"LayoutWidget({self._reactpy_layout})"

    @classmethod
    def _dev(cls) -> None:
        """Load the widget from the dev server"""
        cls._esm = "http://localhost:5173/src/index.js"


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
