from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from appdirs import user_data_dir
from jupyter_server.serverapp import ServerApp
from notebook.base.handlers import AuthenticatedFileHandler
from notebook.notebookapp import NotebookApp

try:
    from reactpy.config import REACTPY_WEB_MODULES_DIR
except ImportError:
    from reactpy.config import REACTPY_WED_MODULES_DIR as REACTPY_WEB_MODULES_DIR


REACTPY_WEB_MODULES_DIR.current = Path(
    user_data_dir("reactpy-jupyter", "reactive-python")
)
REACTPY_WEB_MODULES_DIR.current.mkdir(parents=True, exist_ok=True)
REACTPY_RESOURCE_BASE_PATH = "_reactpy_web_modules"


def _load_jupyter_server_extension(server_app: ServerApp | NotebookApp) -> None:
    web_app = server_app.web_app
    base_url = web_app.settings["base_url"]
    route_pattern = urljoin(base_url, rf"{REACTPY_RESOURCE_BASE_PATH}/(.*)")
    web_app.add_handlers(
        host_pattern=r".*$",
        host_handlers=[
            (
                route_pattern,
                AuthenticatedFileHandler,
                {"path": str(REACTPY_WEB_MODULES_DIR.current.absolute())},
            ),
        ],
    )


# compat for older versions of Jupyter
load_jupyter_server_extension = _load_jupyter_server_extension
