# idom-jupyter

A client for [IDOM](https://github.com/idom-team/idom) implemented using Jupyter widgets

## Try It Now!

Check out a live example by clicking the badge below:

<a href="https://mybinder.org/v2/gh/idom-team/idom-jupyter/main?filepath=notebooks%2Fintroduction.ipynb">
    <img alt="Binder" height="25px" src="https://mybinder.org/badge_logo.svg" />
</a>

## Usage

In a Jupyter Notebook cell, simply create an IDOM layout and use the `idom_jupyter.run`
function to display it:

```python
import idom
import idom_jupyter


@idom.element
def ClickCount():
    count, set_count = idom.hooks.use_state(0)
    return idom.html.button(
        {"onClick": lambda event: set_count(count + 1)},
        [f"Click count: {count}"],
    )


idom_jupyter.run(ClickCount)
```

Alternatively decorate the root of your IDOM layout with `idom_jupyter.widgetize` to
make it return a Jupyter Widget:


```python
import idom
from idom_jupyter import widgetize


@widgetize
@idom.element
def YourRootElement():
    return YourChildElement()


# note how we don't need to widgetize here (only on the root)
@idom.element
def YourChildElement():
    ...


YourRootElement()
```


## Installation

To install use pip:

    $ pip install idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter

To install for jupyterlab

    $ jupyter labextension install idom-client-jupyter

For a development installation (requires npm),

    $ git clone https://github.com/idom-team/idom-jupyter.git
    $ cd idom-jupyter
    $ pip install -e . -r requirements.txt
    $ jupyter serverextension enable --py idom_jupyter
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix idom_jupyter
    $ jupyter nbextension enable --py --sys-prefix idom_jupyter
    $ jupyter labextension install js

When actively developing your extension, build Jupyter Lab with the command:

    $ jupyter lab --watch

This takes a minute or so to get started, but then automatically rebuilds JupyterLab when your javascript changes.

Note on first `jupyter lab --watch`, you may need to touch a file to get Jupyter Lab to open.
