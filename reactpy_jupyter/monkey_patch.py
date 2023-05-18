from typing import Any
from weakref import finalize
from reactpy_jupyter.layout_widget import to_widget
from reactpy.core.component import Component

# we can't track the widgets by adding them as a hidden attribute to the component
# because Component has __slots__ defined
LIVE_WIDGETS: dict[int, Any] = {}


def execute_patch() -> None:
    """Monkey patch ReactPy's Component class to display as a Jupyter widget"""

    def _repr_mimebundle_(self: Component, *a, **kw) -> None:
        self_id = id(self)
        if self_id not in LIVE_WIDGETS:
            widget = LIVE_WIDGETS[self_id] = to_widget(self)
            finalize(self, lambda: LIVE_WIDGETS.pop(self_id, None))
        else:
            widget = LIVE_WIDGETS[self_id]
        return widget._repr_mimebundle_(*a, **kw)

    Component._repr_mimebundle_ = _repr_mimebundle_
