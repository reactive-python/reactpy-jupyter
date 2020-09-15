# idom-jupyter

A client for IDOM implemented using Jupyter widgets

## Try It Now!

Check out a live example by clicking the badge below:

<a href="https://mybinder.org/v2/gh/idom-team/idom-jupyter/master?filepath=notebooks%2Fintroduction.ipynb">
    <img alt="Binder" height="25px" src="https://mybinder.org/badge_logo.svg" />
</a>

## Usage

In a Jupyter Notebook cell, simply create an IDOM layout and use the `idom_jupyter.display`
function to display it:

```python
import idom
from idom_jupyter import display


@idom.element
def ClickCount():
    count, set_count = idom.hooks.use_state(0)

    return idom.html.button(
        {"onClick": lambda event: set_count(count + 1)},
        [f"Click count: {count}"],
    )


display(ClickCount)
```

## Installation

To install use pip:

    $ pip install idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter

To install for jupyterlab

    $ jupyter labextension install idom_jupyter

For a development installation (requires npm),

    $ git clone https://github.com/idom-team/idom-jupyter.git
    $ cd idom-jupyter
    $ pip install -e . -r requirements.txt
    $ jupyter nbextension install --py --symlink --sys-prefix idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter
    $ jupyter labextension install js

When actively developing your extension, build Jupyter Lab with the command:

    $ jupyter lab --watch

This takes a minute or so to get started, but then automatically rebuilds JupyterLab when your javascript changes.

Note on first `jupyter lab --watch`, you may need to touch a file to get Jupyter Lab to open.
