from urllib.parse import urljoin

from appdirs import user_data_dir
from notebook.notebookapp import NotebookApp
from idom.config import IDOM_WED_MODULES_DIR
from tornado.web import StaticFileHandler
from tornado.web import Application


IDOM_WED_MODULES_DIR.current = user_data_dir("idom-jupyter", "idom-team")


def _load_jupyter_server_extension(notebook_app: NotebookApp):
    web_app: Application = notebook_app.web_app
    base_url = web_app.settings["base_url"]
    route_pattern = urljoin(base_url, rf"_idom_web_modules/(.*)")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (
                route_pattern,
                StaticFileHandler,
                {"path": str(IDOM_WED_MODULES_DIR.current.absolute())},
            ),
        ],
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
