from urllib.parse import urljoin

from notebook.notebookapp import NotebookApp
from idom.client.manage import BUILD_DIR
from tornado.web import StaticFileHandler
from tornado.web import Application


def load_jupyter_server_extension(notebook_app: NotebookApp):
    web_app: Application = notebook_app.web_app
    route_pattern = urljoin(web_app.settings["base_url"], "_idom_web_modules/(.*)")
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (
                route_pattern,
                StaticFileHandler,
                {"path": str(BUILD_DIR.absolute() / "web_modules")},
            ),
        ],
    )
