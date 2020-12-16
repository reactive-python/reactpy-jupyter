from ._version import version_info  # noqa
from ._version import __version__  # noqa

from .widget import LayoutWidget, widgetize, run

__all__ = ["LayoutWidget", "widgetize", "run"]


def _jupyter_nbextension_paths():
    """Called by Jupyter Notebook Server to detect if it is a valid nbextension and
    to install the widget

    Returns
    =======
    section: The section of the Jupyter Notebook Server to change.
        Must be 'notebook' for widget extensions
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Notebook copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Notebook copies
        from `src` directory into <jupyter path>/nbextensions/<dest> directory
        during widget installation
    require: Path to importable AMD Javascript module inside the
        <jupyter path>/nbextensions/<dest> directory
    """
    return [
        {
            "section": "notebook",
            "src": "static",
            "dest": "idom-client-jupyter",
            "require": "idom-client-jupyter/extension",
        }
    ]


def _jupyter_server_extension_paths():
    return [{"module": "idom_jupyter.jupyter_server_extension"}]
