from typing import Any
from urllib.parse import urljoin

from appdirs import user_data_dir
from notebook.notebookapp import NotebookApp
from notebook.base.handlers import AuthenticatedFileHandler

from tornado.web import Application

try:
    from idom.config import IDOM_WEB_MODULES_DIR
except ImportError:
    from idom.config import IDOM_WED_MODULES_DIR as IDOM_WEB_MODULES_DIR


IDOM_WEB_MODULES_DIR.current = user_data_dir("idom-jupyter", "idom-team")
IDOM_RESOURCE_BASE_PATH = "_idom_web_modules"


def _load_jupyter_server_extension(notebook_app: NotebookApp):
    web_app: Application = notebook_app.web_app
    base_url = web_app.settings["base_url"]
    route_pattern = urljoin(base_url, rf"{IDOM_RESOURCE_BASE_PATH}/(.*)")
    web_app.add_handlers(
        host_pattern=r".*$",
        host_handlers=[
            (
                route_pattern,
                AuthenticatedFileHandler,
                {"path": str(IDOM_WEB_MODULES_DIR.current.absolute())},
            ),
        ],
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
