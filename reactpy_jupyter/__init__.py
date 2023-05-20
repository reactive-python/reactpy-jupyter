#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ryan Morshead.
# Distributed under the terms of the Modified BSD License.

from . import jupyter_server_extension
from .component_widget import run, set_import_source_base_url, to_widget
from .hooks import use_trait
from .import_resources import setup_import_resources
from .monkey_patch import execute_patch
from .widget_component import from_widget

__version__ = "0.9.5"  # DO NOT MODIFY

__all__ = (
    "from_widget",
    "jupyter_server_extension",
    "load_ipython_extension",
    "run",
    "set_import_source_base_url",
    "to_widget",
    "unload_ipython_extension",
    "use_trait",
)


setup_import_resources()
execute_patch()
