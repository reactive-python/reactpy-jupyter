from idom.client.manage import BUILD_DIR
from tornado.web import StaticFileHandler
from tornado.web import Application


def load_jupyter_server_extension(notebook_app):
    web_app: Application = notebook_app.web_app
    web_app.add_handlers(
        host_pattern=".*$",
        host_handlers=[
            (
                "/_idom_web_modules/(.*)",
                StaticFileHandler,
                {"path": str(BUILD_DIR.absolute() / "web_modules")},
            ),
        ],
    )
