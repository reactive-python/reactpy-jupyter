from __future__ import annotations

from typing import Callable

from attr import dataclass
from ipywidgets import Widget
from reactpy import component, create_context, html, use_context, use_effect
from reactpy.types import Context, VdomDict

inner_widgets_context: Context[InnerWidgets | None] = create_context(None)


@component
def from_widget(source: Widget) -> VdomDict:
    inner_widgets = use_context(inner_widgets_context)

    @use_effect
    def add_widget():
        inner_widgets.add(source)
        return lambda: inner_widgets.remove(source)

    if inner_widgets is None:
        raise RuntimeError("Jupyter component must be rendered inside a JupyterLayout")

    return html.span({"class": f"widget-model-id-{source.model_id}"})


@dataclass
class InnerWidgets:
    add: Callable[[Widget], None]
    remove: Callable[[Widget], None]
