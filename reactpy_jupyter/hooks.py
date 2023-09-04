from typing import Any

from reactpy import use_effect, use_state
from reactpy.types import State
from traitlets import HasTraits


def use_trait(obj: HasTraits, name: str) -> State[Any]:
    """Hook to use the attribute of a HasTraits object as a state variable

    This works on Jupyter Widgets, for example.
    """
    value, set_value = use_state(lambda: getattr(obj, name))

    @use_effect
    def register_observer():
        def handle_change(change):
            set_value(change["new"])

        # observe the slider's value
        obj.observe(handle_change, "value")
        # unobserve the slider's value if this component is no longer displayed
        return lambda: obj.unobserve(handle_change, "value")

    def set_trait(new_value: Any) -> None:
        setattr(obj, name, new_value)

    return State(value, set_trait)
