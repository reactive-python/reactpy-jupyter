from __future__ import annotations

import logging
import socket
from contextlib import closing
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from uuid import uuid4

import requests
from notebook import notebookapp

from .jupyter_server_extension import (
    REACTPY_RESOURCE_BASE_PATH,
    REACTPY_WEB_MODULES_DIR,
)
from .widget import set_import_source_base_url

logger = logging.getLogger(__name__)


def setup_import_resources() -> None:
    if _try_to_set_import_source_base_url():
        return None

    host = "127.0.0.1"
    port = _find_available_port("127.0.0.1")

    logger.debug(
        f"Serving web modules via local static file server at http://{host}:{port}/"
    )
    serve_dir = str(REACTPY_WEB_MODULES_DIR.current)

    thread = Thread(
        target=_run_simple_static_file_server,
        args=(host, port, serve_dir),
        daemon=True,
    )
    thread.start()

    set_import_source_base_url(f"http://{host}:{port}/")


def _try_to_set_import_source_base_url() -> bool:
    # Try to see if there's a local server we should use. This might happen when running
    # in a notebook from within VSCode
    _temp_file_name = f"__temp_{uuid4().hex}__"
    _temp_file = REACTPY_WEB_MODULES_DIR.current / _temp_file_name
    _temp_file.touch()
    for _server_info in notebookapp.list_running_servers():
        if _server_info["hostname"] not in ("localhost", "127.0.0.1"):
            continue

        _resource_url_parts = [
            _server_info["url"].rstrip("/"),
            _server_info["base_url"].strip("/"),
            REACTPY_RESOURCE_BASE_PATH,
        ]
        _resource_url = "/".join(filter(None, _resource_url_parts))
        _temp_file_url = _resource_url + "/" + _temp_file_name

        response = requests.get(_temp_file_url, params={"token": _server_info["token"]})

        if response.status_code == 200:
            set_import_source_base_url(_resource_url)
            logger.debug(
                f"Serving web modules via existing NotebookApp server at {_resource_url!r}"
            )
            return True
    _temp_file.unlink()
    return False


def _run_simple_static_file_server(host: str, port: int, directory: str) -> None:
    class CORSRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            SimpleHTTPRequestHandler.end_headers(self)

        def log_message(self, format, *args):
            logger.info(
                "%s - - [%s] %s\n"
                % (self.address_string(), self.log_date_time_string(), format % args)
            )

    def make_cors_handler(*args, **kwargs):
        return CORSRequestHandler(*args, directory=directory, **kwargs)

    with HTTPServer((host, port), make_cors_handler) as httpd:
        httpd.serve_forever()


def _find_available_port(
    host: str,
    port_min: int = 8000,
    port_max: int = 9000,
    allow_reuse_waiting_ports: bool = True,
) -> int:
    """Get a port that's available for the given host and port range"""
    for port in range(port_min, port_max):
        with closing(socket.socket()) as sock:
            try:
                if allow_reuse_waiting_ports:
                    # As per this answer: https://stackoverflow.com/a/19247688/3159288
                    # setting can be somewhat unreliable because we allow the use of
                    # ports that are stuck in TIME_WAIT. However, not setting the option
                    # means we're overly cautious and almost always use a different addr
                    # even if it could have actually been used.
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, port))
            except OSError:
                pass
            else:
                return port
    raise RuntimeError(
        f"Host {host!r} has no available port in range {port_max}-{port_max}"
    )
