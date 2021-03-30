from urllib.parse import urljoin

from notebook.notebookapp import NotebookApp
from idom.config import IDOM_CLIENT_BUILD_DIR
from tornado.web import StaticFileHandler
from tornado.web import Application


def _load_jupyter_server_extension(notebook_app: NotebookApp):
    web_app: Application = notebook_app.web_app
    base_url = web_app.settings["base_url"]
    route_pattern = urljoin(base_url, r"_idom_web_modules/(.*)")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (
                route_pattern,
                StaticFileHandler,
                {"path": str(IDOM_CLIENT_BUILD_DIR.get().absolute())},
            ),
        ],
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
