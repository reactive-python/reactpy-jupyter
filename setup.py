from __future__ import annotations

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from pathlib import Path

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
)

# --------------------------------------------------------------------------------------
# Common Constants
# --------------------------------------------------------------------------------------

NAME = "idom_jupyter"
ROOT_DIR = Path(__file__).resolve().parent

# --------------------------------------------------------------------------------------
# Package Definition
# --------------------------------------------------------------------------------------

package = dict(
    name=NAME,
    description="A client for IDOM implemented using Jupyter widgets",
    include_package_data=True,
    install_requires=[
        "ipywidgets>=7.6.0",
        "idom>=0.42,<0.43",
        "appdirs",
        "requests",
        "jupyter_server",
        "notebook",
        "typing_extensions",
    ],
    packages=find_packages(),
    zip_safe=False,
    author="Ryan Morshead",
    author_email="ryan.morshead@gmail.com",
    url="https://github.com/idom-team/idom-jupyter",
    keywords=[
        "ipython",
        "jupyter",
        "widgets",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: IPython",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

# --------------------------------------------------------------------------------------
# Python Package Version
# --------------------------------------------------------------------------------------

_version_module = {}
exec((ROOT_DIR / NAME / "_version.py").read_text(), _version_module)
package["version"] = _version_module["__version__"]

# --------------------------------------------------------------------------------------
# Long Description
# --------------------------------------------------------------------------------------

package["long_description"] = (ROOT_DIR / "README.md").read_text()
package["long_description_content_type"] = "text/markdown"

# --------------------------------------------------------------------------------------
# Build Javascript
# --------------------------------------------------------------------------------------

JS_DIR = ROOT_DIR / "js"

# Representative files that should exist after a successful build
jstargets = [JS_DIR / "dist" / "index.js"]

data_files_spec = [
    (
        "share/jupyter/nbextensions/idom-client-jupyter",
        "idom_jupyter/nbextension",
        "*.*",
    ),
    (
        "share/jupyter/labextensions/idom-client-jupyter",
        "idom_jupyter/labextension",
        "**",
    ),
    (
        "share/jupyter/labextensions/idom-client-jupyter",
        ".",
        "install.json",
    ),
    (
        "etc/jupyter",
        "jupyter-config",
        "**",
    ),
]

cmdclass = create_cmdclass("jsdeps", data_files_spec=data_files_spec)
cmdclass["jsdeps"] = combine_commands(
    install_npm(JS_DIR, npm=["yarn"], build_cmd="build:prod"),
    ensure_targets(jstargets),
)
package["cmdclass"] = cmdclass

# -----------------------------------------------------------------------------
# Install It
# -----------------------------------------------------------------------------

setup(**package)
