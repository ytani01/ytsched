#
# (c) 2021 Yoichi Tanibayashi
#
"""
YT scheduler
"""
from importlib.metadata import PackageNotFoundError, version

__author__ = 'Yoichi Tanibayashi'

if __package__:
    try:
        __version__ = version(__package__)
    except PackageNotFoundError:
        __version__ = '0.0.0'
else:
    __version__ = '_._._'

__prog_name__ = 'Ytsched'

from .ytsched import SchedDataEnt, SchedDataFile, SchedData
from .webapp import WebServer
from .main_handler import MainHandler

__all__ = [
    '__author__', '__version__', '__prog_name__',
    'SchedDataEnt', 'SchedDataFile', 'SchedData',
    'WebServer', 'MainHandler'
]
