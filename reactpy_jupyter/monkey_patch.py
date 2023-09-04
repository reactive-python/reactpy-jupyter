from reactpy.core.component import Component

from reactpy_jupyter.widget_component import WidgetComponent


def execute_patch() -> None:
    """Monkey patch ReactPy's Component class to display as a Jupyter widget"""
    Component._repr_mimebundle_ = WidgetComponent._repr_mimebundle_
