#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for musicbox package
"""

import datetime

import click

from . import MainHandler, SchedDataFile, WebServer, __prog_name__
from .migrate import Migrator
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
                print(f"{sde.mk_dataline()}")
        else:
            print("===== No data =====")


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


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
    help=f"data directory, default='{SchedDataFile.DEF_TOP_DIR}'",
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
        _log.info("end")


@cli.command(
    help="""
旧形式(タブ区切り .cgi)のデータを JSON Lines (.jsonl) へ変換する

元の .cgi は消さない。既に .jsonl があるファイルは飛ばす。
"""
)
@click.option(
    "--datadir",
    "--data",
    "datadir",
    type=click.Path(),
    default=SchedDataFile.DEF_TOP_DIR,
    help=f"data directory, default='{SchedDataFile.DEF_TOP_DIR}'",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    default=False,
    help="書き出さずに、件数だけ出す",
)
@click.option(
    "--error-file",
    "error_file",
    type=click.Path(),
    default=Migrator.DEF_ERROR_FILE,
    help=(
        f"変換できなかった行の書き出し先, default='{Migrator.DEF_ERROR_FILE}'"
    ),
)
@click.option(
    "--debug", "-d", "debug", is_flag=True, default=False, help="debug flag"
)
def migrate(datadir, dry_run, error_file, debug):
    """migrate"""
    loggerInit(debug=debug)

    app = Migrator(datadir, dry_run=dry_run, error_file=error_file)
    try:
        app.main()
    finally:
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
    help=f"port number, default={WebServer.DEF_PORT}",
)
@click.option(
    "--webroot",
    "-r",
    "webroot",
    type=click.Path(exists=True),
    default=WebServer.DEF_WEBROOT,
    help=f"Web root directory, default='{WebServer.DEF_WEBROOT}'",
)
@click.option(
    "--datadir",
    "-w",
    "datadir",
    type=click.Path(),
    default=WebServer.DEF_DATADIR,
    help=f"data directory, default='{WebServer.DEF_DATADIR}'",
)
@click.option(
    "--days",
    "days",
    type=int,
    default=MainHandler.DEF_DAYS,
    help=f"+/- days, default={MainHandler.DEF_DAYS}",
)
@click.option(
    "--size_limit",
    "-l",
    "size_limit",
    type=int,
    default=100 * 1024 * 1024,
    help=f"upload size limit, default={WebServer.DEF_SIZE_LIMIT}",
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
