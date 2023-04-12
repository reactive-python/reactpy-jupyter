#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Ryan Morshead.
# Distributed under the terms of the Modified BSD License.

from . import jupyter_server_extension
from .import_resources import setup_import_resources
from .widget import LayoutWidget, widgetize, run, set_import_source_base_url
from .ipython_extension import load_ipython_extension, unload_ipython_extension

__version__ = "0.8.0"  # DO NOT MODIFY

__all__ = [
    "LayoutWidget",
    "widgetize",
    "run",
    "load_ipython_extension",
    "unload_ipython_extension",
    "set_import_source_base_url",
    "jupyter_server_extension",
]


setup_import_resources()
