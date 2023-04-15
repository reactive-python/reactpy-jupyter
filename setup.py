from __future__ import print_function

import pipes
import shutil
import subprocess
import sys
import traceback
from logging import StreamHandler, getLogger
from pathlib import Path

from jupyter_packaging import get_data_files
from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist

if sys.platform == "win32":
    from subprocess import list2cmdline
else:

    def list2cmdline(cmd_list):
        return " ".join(map(pipes.quote, cmd_list))


log = getLogger()
log.addHandler(StreamHandler(sys.stdout))


# --------------------------------------------------------------------------------------
# Basic Constants
# --------------------------------------------------------------------------------------


# the name of the project
NAME = "reactpy_jupyter"

# basic paths used to gather files
ROOT_DIR = Path(__file__).parent


# --------------------------------------------------------------------------------------
# Package Definition
# --------------------------------------------------------------------------------------


package = {
    "name": NAME,
    "python_requires": ">=3.7",
    "packages": find_packages(ROOT_DIR, include="reactpy_jupyter.*"),
    "description": "It's React, but in Python",
    "author": "Ryan Morshead",
    "author_email": "ryan.morshead@gmail.com",
    "url": "https://github.com/reactive-python/reactpy",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": ["interactive", "widgets", "DOM", "React"],
    "include_package_data": True,
    "zip_safe": False,
    "classifiers": [
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Widget Sets",
        "Typing :: Typed",
    ],
}


# --------------------------------------------------------------------------------------
# Library Version
# --------------------------------------------------------------------------------------

pkg_root_init_file = ROOT_DIR / NAME / "__init__.py"
for line in pkg_root_init_file.read_text().split("\n"):
    if line.startswith('__version__ = "') and line.endswith('"  # DO NOT MODIFY'):
        package["version"] = (
            line
            # get assignment value
            .split("=", 1)[1]
            # remove "DO NOT MODIFY" comment
            .split("#", 1)[0]
            # clean up leading/trailing space
            .strip()
            # remove the quotes
            [1:-1]
        )
        break
else:
    print(f"No version found in {pkg_root_init_file}")
    sys.exit(1)


# --------------------------------------------------------------------------------------
# Requirements
# --------------------------------------------------------------------------------------

package["install_requires"] = [
    "anywidget<1",
    "reactpy>=1.0.0",
    "appdirs",
    "requests",
    "jupyter_server",
    "notebook",
    "typing_extensions",
]

# --------------------------------------------------------------------------------------
# Library Description
# --------------------------------------------------------------------------------------


with (ROOT_DIR / "README.md").open() as f:
    long_description = f.read()

package["long_description"] = long_description
package["long_description_content_type"] = "text/markdown"


# --------------------------------------------------------------------------------------
# Jupyter Config Data Files
# --------------------------------------------------------------------------------------

package["data_files"] = get_data_files(
    [
        (
            "etc/jupyter",
            "jupyter-config",
            "**",
        ),
    ]
)

# --------------------------------------------------------------------------------------
# Build Javascript
# --------------------------------------------------------------------------------------


def build_javascript_first(cls):
    class Command(cls):
        def run(self):
            log.info("Installing Javascript...")
            try:
                npm = shutil.which("npm")  # this is required on windows
                if npm is None:
                    raise RuntimeError("NPM is not installed.")
                for args in (f"{npm} ci", f"{npm} run build"):
                    args_list = args.split()
                    log.info(f"> {list2cmdline(args_list)}")
                    subprocess.run(args_list, cwd=str(ROOT_DIR), check=True)
            except Exception:
                log.error("Failed to install Javascript")
                log.error(traceback.format_exc())
                raise
            else:
                log.info("Successfully installed Javascript")
            super().run()

    return Command


package["cmdclass"] = {
    "sdist": build_javascript_first(sdist),
    "develop": build_javascript_first(develop),
}

if sys.version_info < (3, 10, 6):
    from distutils.command.build import build

    package["cmdclass"]["build"] = build_javascript_first(build)
else:
    from setuptools.command.build_py import build_py

    package["cmdclass"]["build_py"] = build_javascript_first(build_py)


# --------------------------------------------------------------------------------------
# Install It
# --------------------------------------------------------------------------------------


if __name__ == "__main__":
    setup(**package)
