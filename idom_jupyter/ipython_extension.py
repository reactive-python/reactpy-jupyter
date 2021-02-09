from functools import partial

from idom.core.component import AbstractComponent
from IPython import get_ipython
from IPython.display import display

from .widget import LayoutWidget


_EXTENSION_LOADED = False
_POST_RUN_CELL_HOOK = None


def load_ipython_extension(ipython):
    global _POST_RUN_CELL_HOOK, _EXTENSION_LOADED
    if not _EXTENSION_LOADED:
        _POST_RUN_CELL_HOOK = partial(_post_run_cell, ipython)
        ipython.events.register("post_run_cell", _POST_RUN_CELL_HOOK)
        ipython.display_formatter.ipython_display_formatter.for_type(
            AbstractComponent, lambda element: ({}, {})
        )
        _EXTENSION_LOADED = True


def unload_ipython_extension(ipython):
    global _POST_RUN_CELL_HOOK, _EXTENSION_LOADED
    ipython.events.unregister("post_run_cell", _POST_RUN_CELL_HOOK)
    _POST_RUN_CELL_HOOK = None
    _EXTENSION_LOADED = False


def _post_run_cell(ipython, result):
    if isinstance(result.result, AbstractComponent):
        display(LayoutWidget(result.result))


if get_ipython() is not None:
    load_ipython_extension(get_ipython())
