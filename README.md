idom-jupyter
===============================

A client for IDOM implemented using Jupyter widgets

Installation
------------

To install use pip:

    $ pip install idom-jupyter
    $ jupyter nbextension enable --py --sys-prefix idom-jupyter

To install for jupyterlab

    $ jupyter labextension install idom-jupyter

For a development installation (requires npm),

    $ git clone https://github.com/idom-team/idom-jupyter.git
    $ cd idom-jupyter
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix idom-jupyter
    $ jupyter nbextension enable --py --sys-prefix idom-jupyter
    $ jupyter labextension install js

When actively developing your extension, build Jupyter Lab with the command:

    $ jupyter lab --watch

This takes a minute or so to get started, but then automatically rebuilds JupyterLab when your javascript changes.

Note on first `jupyter lab --watch`, you may need to touch a file to get Jupyter Lab to open.

