# idom-jupyter

A client for [IDOM](https://github.com/idom-team/idom) implemented using Jupyter widgets

## Try It Now!

Check out a live example by clicking the badge below:

<a href="https://mybinder.org/v2/gh/idom-team/idom-jupyter/main?filepath=notebooks%2Fintroduction.ipynb">
    <img alt="Binder" height="25px" src="https://mybinder.org/badge_logo.svg" />
</a>

## Getting Started

To install use `pip`:

```
pip install idom_jupyter
```

Then, before anything else, do one of the following:

1. At the top of your notebook run

   ```python
   import idom_jupyter
   ```

2. Register `idom_jupyter` as a permanant IPython extension in [your config file](https://ipython.readthedocs.io/en/stable/config/intro.html#introduction-to-ipython-configuration):

   ```python
   c.InteractiveShellApp.extensions = [
       'idom_jupyter'
   ]
   ```

## Usage

Once you're done [getting started](#getting-started), you can author and display IDOM
layouts natively in your Jupyter Notebook:

```python
import idom

@idom.component
def ClickCount():
    count, set_count = idom.hooks.use_state(0)
    return idom.html.button(
        {"onClick": lambda event: set_count(count + 1)},
        [f"Click count: {count}"],
    )

ClickCount()
```

You can also turn an `idom` element constructor into one that returns an `ipywidget` with
the `idom_juptyer.widgetize` function. This is useful if you wish to use IDOM in combination
with other Jupyter Widgets as in the following example:

```python
ClickCountWidget = idom_jupyter.widgetize(ClickCount)
ipywidgets.Box(
    [
        ClickCountWidget(),
        ClickCountWidget(),
    ]
)
```

Alternatively just wrap an `idom` element instance in an `idom_jupyter.LayoutWidget`:

```python
ipywidgets.Box(
    [
        idom_jupyter.LayoutWidget(ClickCount()),
        idom_jupyter.LayoutWidget(ClickCount()),
    ]
)
```

# Development Installation

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

```
git clone https://github.com/idom-team/idom-jupyter.git
cd idom-jupyter
pip install -e . -r requirements.txt
jupyter nbextension install --py --symlink --overwrite --sys-prefix idom_jupyter
jupyter nbextension enable --py --sys-prefix idom_jupyter
```

When actively developing your extension for JupyterLab, run the command:

```
jupyter labextension develop --overwrite idom_jupyter
```

Then you need to rebuild the JS when you make a code change:

```
cd js
yarn run build
```

You then need to refresh the JupyterLab page when your javascript changes.
