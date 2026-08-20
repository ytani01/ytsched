#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for musicbox package
"""

import datetime

import click

from . import MainHandler, SchedDataFile, WebServer, __prog_name__
from .mylog import getLogger, loggerInit

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

_log = getLogger("main")


class DataFileApp:
    __log = getLogger(__qualname__)

    def __init__(self, yyyy, mm, dd, topdir=""):
        self.__log.debug(f"yyyy/mm/dd={yyyy}/{mm}/{dd}")
        self.__log.debug(f"topdir={topdir}")

        self.sdf = SchedDataFile(datetime.date(yyyy, mm, dd), topdir=topdir)

    def main(self):
        self.__log.debug(f"sdf.sde={self.sdf.sde}")

        if self.sdf.sde:
            for sde in sorted(self.sdf.sde, key=lambda x: x.get_timestr()):
                print(sde)
                print("%s" % (sde.mk_dataline().replace("\t", "<tab>")))
        else:
            print("===== No data =====")

    def end(self):
        self.__log.debug("")


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    help="""
sample package
""",
)
@click.pass_context
def cli(ctx):
    """command group"""
    subcmd = ctx.invoked_subcommand

    if subcmd is None:
        print(ctx.get_help())


@cli.command(
    help="""
test """
)
@click.argument("year", type=int, default=2021)
@click.argument("month", type=int, default=1)
@click.argument("day", type=int, default=1)
@click.option(
    "--datadir",
    "--data",
    "datadir",
    type=click.Path(exists=True),
    default=SchedDataFile.DEF_TOP_DIR,
    help="data directory, default='%s'" % (SchedDataFile.DEF_TOP_DIR),
)
@click.option(
    "--debug", "-d", "debug", is_flag=True, default=False, help="debug flag"
)
def x_data1(year, month, day, datadir, debug):
    """data"""
    loggerInit(debug=debug)

    app = DataFileApp(year, month, day, datadir)
    try:
        app.main()
    finally:
        _log.debug("finally")
        app.end()
        _log.info("end")


@cli.command(
    help="""
Web server"""
)
@click.option(
    "--port",
    "-p",
    "port",
    type=int,
    default=WebServer.DEF_PORT,
    help="port number, default=%s" % (WebServer.DEF_PORT),
)
@click.option(
    "--webroot",
    "-r",
    "webroot",
    type=click.Path(exists=True),
    default=WebServer.DEF_WEBROOT,
    help="Web root directory, default='%s'" % (WebServer.DEF_WEBROOT),
)
@click.option(
    "--datadir",
    "-w",
    "datadir",
    type=click.Path(),
    default=WebServer.DEF_DATADIR,
    help="data directory, default='%s'" % (WebServer.DEF_DATADIR),
)
@click.option(
    "--days",
    "days",
    type=int,
    default=MainHandler.DEF_DAYS,
    help="+/- days, default=%s" % (MainHandler.DEF_DAYS),
)
@click.option(
    "--size_limit",
    "-l",
    "size_limit",
    type=int,
    default=100 * 1024 * 1024,
    help="upload size limit, default=%s" % (WebServer.DEF_SIZE_LIMIT),
)
@click.option(
    "--version",
    "-v",
    "version",
    is_flag=True,
    default=False,
    help="print version",
)
@click.option(
    "--debug", "-d", "debug", is_flag=True, default=False, help="debug flag"
)
def webapp(port, webroot, datadir, days, size_limit, version, debug):
    """webapp"""
    loggerInit(debug=debug)

    app = WebServer(
        port, webroot, datadir, days, size_limit, version, debug=debug
    )
    try:
        app.main()
    finally:
        _log.info("end")


if __name__ == "__main__":
    cli(prog_name=__prog_name__)
