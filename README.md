# idom-jupyter

A client for IDOM implemented using Jupyter widgets

## Installation

To install use pip:

    $ pip install idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter

To install for jupyterlab

    $ jupyter labextension install idom_jupyter

For a development installation (requires npm),

    $ git clone https://github.com/idom-team/idom-jupyter.git
    $ cd idom-jupyter
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter
    $ jupyter labextension install js

When actively developing your extension, build Jupyter Lab with the command:

    $ jupyter lab --watch

This takes a minute or so to get started, but then automatically rebuilds JupyterLab when your javascript changes.

Note on first `jupyter lab --watch`, you may need to touch a file to get Jupyter Lab to open.
