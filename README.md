idom-jupyter
===============================

A client for IDOM implemented using Jupyter widgets

Installation
------------

To install use pip:

    $ pip install idom_jupyter

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/idom-team/idom-jupyter.git
    $ cd idom-jupyter
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite idom_jupyter

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
