from __future__ import print_function
from setuptools import setup, find_packages
import os
from os.path import join as pjoin
from distutils import log

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)


here = os.path.dirname(os.path.abspath(__file__))

log.set_verbosity(log.DEBUG)
log.info("setup.py entered")
log.info("$PATH=%s" % os.environ["PATH"])

name = "idom_jupyter"

with open(os.path.join(here, "README.md")) as f:
    LONG_DESCRIPTION = f.read()

# Get idom_jupyter version
version = get_version(pjoin(name, "_version.py"))

js_dir = pjoin(here, "js")

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, "dist", "index.js"),
]

data_files_spec = [
    (
        "share/jupyter/nbextensions/idom-client-jupyter",
        "idom_jupyter/nbextension",
        "*.*",
    ),
    (
        "share/jupyter/labextensions/idom-client-jupyter",
        "idom_jupyter/labextension",
        "*.*",
    ),
    ("etc/jupyter/nbconfig/notebook.d", ".", "idom-client-jupyter.json"),
]

cmdclass = create_cmdclass("jsdeps", data_files_spec=data_files_spec)
cmdclass["jsdeps"] = combine_commands(
    install_npm(js_dir, build_cmd="build"),
    ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    version=version,
    description="A client for IDOM implemented using Jupyter widgets",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "ipywidgets>=7.0.0",
    ],
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)

setup(**setup_args)
