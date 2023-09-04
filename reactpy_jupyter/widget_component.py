from __future__ import annotations

from typing import Any, Callable
from weakref import finalize

from attr import dataclass
from ipywidgets import Widget
from reactpy import create_context, html, use_context, use_effect
from reactpy.types import Context, Key, State, VdomDict

import reactpy_jupyter
from reactpy_jupyter.hooks import use_trait as _use_trait

# we can't track the widgets by adding them as a hidden attribute to the component
# because Component has __slots__ defined
LIVE_WIDGETS: dict[int, Any] = {}

inner_widgets_context: Context[InnerWidgets | None] = create_context(None)


def from_widget(source: Widget, key: Key | None = None) -> WidgetComponent:
    return WidgetComponent(source, key)


class WidgetComponent:
    """implements reactpy.types.ComponentType"""

    def __init__(self, widget: Widget, key: Key | None) -> None:
        self.widget = widget
        self.type = type(widget)
        self.key = key

    def use_trait(self, name: str) -> State[Any]:
        return _use_trait(self.widget, name)

    def render(self) -> VdomDict:
        inner_widgets = use_context(inner_widgets_context)

        @use_effect
        def add_widget():
            inner_widgets.add(self.widget)
            return lambda: inner_widgets.remove(self.widget)

        if inner_widgets is None:
            raise RuntimeError(
                "Jupyter component must be rendered inside a JupyterLayout"
            )

        return html.span({"class": f"widget-model-id-{self.widget.model_id}"})

    def _repr_mimebundle_(self, *args: Any, **kwargs: Any) -> None:
        self_id = id(self)
        if self_id not in LIVE_WIDGETS:
            widget = LIVE_WIDGETS[self_id] = reactpy_jupyter.to_widget(self)
            finalize(self, lambda: LIVE_WIDGETS.pop(self_id, None))
        else:
            widget = LIVE_WIDGETS[self_id]
        return widget._repr_mimebundle_(*args, **kwargs)


@dataclass
class InnerWidgets:
    add: Callable[[Widget], None]
    remove: Callable[[Widget], None]
