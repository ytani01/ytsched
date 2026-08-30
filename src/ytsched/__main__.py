#
# (c) 2026 ytani01
#
"""
main for ytsched package
"""

import click

from . import __prog_name__, __version__
from .click_utils import click_common_opts
from .holiday import DEF_URL, HolidayRegistrar
from .migrate import Migrator
from .mylog import getLogger, loggerInit
from .webapp import WebServer
from .ytsched import SchedDataFile

__author__ = "ytani01"
__date__ = "2021/01"

_log = getLogger("main")


def _is_debug(ctx, debug):
    """自分の --debug と、グループ側の --debug をまとめる

    `cli` を経由しない呼び出しでは `ctx.obj` が None になるので、
    dict のときだけ見る。
    """
    if isinstance(ctx.obj, dict):
        return bool(debug) or bool(ctx.obj.get("debug", False))

    return bool(debug)


@click.group(
    invoke_without_command=True,
    help="""
YT scheduler
""",
)
@click_common_opts(__version__)
def cli(ctx, debug):
    """command group"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = bool(debug)

    loggerInit(debug=debug)

    subcmd = ctx.invoked_subcommand

    if subcmd is None:
        print(ctx.get_help())


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
@click_common_opts(__version__)
def migrate(ctx, datadir, dry_run, error_file, debug):
    """migrate"""
    debug = _is_debug(ctx, debug)
    loggerInit(debug=debug)

    app = Migrator(datadir, dry_run=dry_run, error_file=error_file)
    try:
        app.main()
    finally:
        _log.info("end")


@cli.command(
    help="""
内閣府の CSV から日本の祝日を取得して登録する

年を 1 つ以上指定する。同じ日付・同じ名称の予定が既にあれば飛ばす。
指定した年が CSV に無ければ、その年は飛ばして他の年は続ける。
"""
)
@click.argument("years", type=int, nargs=-1, required=True)
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
    "--url",
    "url",
    type=str,
    default=DEF_URL,
    help=f"取得元の URL, default='{DEF_URL}'",
)
@click_common_opts(__version__)
def holiday(ctx, years, datadir, dry_run, url, debug):
    """holiday"""
    debug = _is_debug(ctx, debug)
    loggerInit(debug=debug)

    app = HolidayRegistrar(datadir, list(years), dry_run=dry_run, url=url)
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
    "--urlprefix",
    "-u",
    "urlprefix",
    type=str,
    default=WebServer.DEF_URL_PREFIX,
    help=f"URL prefix, default='{WebServer.DEF_URL_PREFIX}'",
)
@click.option(
    "--size-limit",
    "-l",
    "size_limit",
    type=int,
    default=WebServer.DEF_SIZE_LIMIT,
    help=f"upload size limit, default={WebServer.DEF_SIZE_LIMIT}",
)
@click_common_opts(__version__)
def webapp(ctx, port, webroot, datadir, urlprefix, size_limit, debug):
    """webapp"""
    debug = _is_debug(ctx, debug)
    loggerInit(debug=debug)
    _log.debug(f"urlprefix={urlprefix}")

    app = WebServer(
        port,
        webroot,
        datadir,
        urlprefix,
        size_limit,
        debug=debug,
    )
    try:
        app.main()
    finally:
        _log.info("end")


if __name__ == "__main__":
    cli(prog_name=__prog_name__)
