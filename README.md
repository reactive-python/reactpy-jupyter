# reactpy-jupyter

A client for [ReactPy](https://github.com/reactive-python/reactpy) implemented using Jupyter widgets

## Try It Now!

Check out some live examples by clicking the badge below:

<a href="https://mybinder.org/v2/gh/reactive-python/reactpy-jupyter/main?urlpath=lab%2Ftree%2Fnotebooks%2Fintroduction.ipynb">
    <img alt="Binder" height="25px" src="https://mybinder.org/badge_logo.svg" />
</a>

## Getting Started

To install use `pip`:

```
pip install reactpy_jupyter
```

Then, before anything else, do one of the following:

1. At the top of your notebook run

   ```python
   import reactpy_jupyter
   ```

2. Register `reactpy_jupyter` as a permanant IPython extension in [your config file](https://ipython.readthedocs.io/en/stable/config/intro.html#introduction-to-ipython-configuration):

   ```python
   c.InteractiveShellApp.extensions = [
       'reactpy_jupyter'
   ]
   ```

## Usage

Once you're done [getting started](#getting-started), you can author and display ReactPy
layouts natively in your Jupyter Notebook:

```python
import reactpy

@reactpy.component
def ClickCount():
    count, set_count = reactpy.hooks.use_state(0)
    return reactpy.html.button(
        {"onClick": lambda event: set_count(count + 1)},
        [f"Click count: {count}"],
    )

ClickCount()
```

You can also turn an `reactpy` element constructor into one that returns an `ipywidget` with
the `reactpy_juptyer.widgetize` function. This is useful if you wish to use ReactPy in combination
with other Jupyter Widgets as in the following example:

```python
ClickCountWidget = reactpy_jupyter.widgetize(ClickCount)
ipywidgets.Box(
    [
        ClickCountWidget(),
        ClickCountWidget(),
    ]
)
```

Alternatively just wrap an `reactpy` element instance in an `reactpy_jupyter.LayoutWidget`:

```python
ipywidgets.Box(
    [
        reactpy_jupyter.LayoutWidget(ClickCount()),
        reactpy_jupyter.LayoutWidget(ClickCount()),
    ]
)
```

For a more detailed introduction check out this live demo here:

<a href="https://mybinder.org/v2/gh/reactive-python/reactpy-jupyter/main?filepath=notebooks%2Fintroduction.ipynb">
    <img alt="Binder" height="25px" src="https://mybinder.org/badge_logo.svg" />
</a>

## Development Installation

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/reactive-python/reactpy-jupyter.git
    $ cd reactpy-jupyter
    $ pip install -e .

To automatically re-build and refresh Jupyter when making changes start a Vite dev server:

    $ npx vite

Then, before importing `reactpy_jupyter` set the following environment variable:

```python
import os
os.environ["REACTPY_JUPYTER_DEV"] = "1"
import reactpy_jupyter
```
