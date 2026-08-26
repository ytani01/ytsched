#
# (c) 2026 ytani01
#
"""
YT scheduler
"""

from importlib.metadata import PackageNotFoundError, version

__author__ = "ytani01"

if __package__:
    try:
        __version__ = version(__package__)
    except PackageNotFoundError:
        __version__ = "0.0.0"
else:
    __version__ = "_._._"

__prog_name__ = "Ytsched"

from .main_handler import MainHandler
from .webapp import WebServer
from .ytsched import SchedData, SchedDataEnt, SchedDataFile

__all__ = [
    "MainHandler",
    "SchedData",
    "SchedDataEnt",
    "SchedDataFile",
    "WebServer",
    "__author__",
    "__prog_name__",
    "__version__",
]
