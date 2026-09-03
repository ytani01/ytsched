#
# (c) 2026 ytani01
#
"""
main for ytsched package
"""

import datetime

import click

from . import __prog_name__, __version__
from .click_utils import click_common_opts
from .fix_id import IdFixer
from .holiday import DEF_URL, HolidayRegistrar
from .migrate import Migrator
from .mylog import getLogger, loggerInit
from .notify import build_notify_text
from .webapp import WebServer
from .ytsched import SchedData, SchedDataFile

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
    name="fix-id",
    help="""
予定の sde_id を UUID へ振り直す

旧形式から移ってきた sde_id は独自の形のまま残っている。UUID でない
sde_id だけを新しい UUID へ差し替えて書き戻す。元に戻せないので、
まず --dry-run で件数を確かめてから実行すること。
""",
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
@click_common_opts(__version__)
def fix_id(ctx, datadir, dry_run, debug):
    """fix-id"""
    debug = _is_debug(ctx, debug)
    loggerInit(debug=debug)

    app = IdFixer(datadir, dry_run=dry_run)
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


@cli.command(
    help="""
その日の予定と、期限の近い ToDo をテキストで標準出力へ出す

Slack へ送るのはこのコマンドの役目ではない。出したテキストを
別の道具（``slack-send.sh`` など）へパイプすること。
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
    "--date",
    "date_str",
    type=str,
    default=None,
    help="対象の日 (YYYY-MM-DD), default=今日",
)
@click.option(
    "--no-todo",
    "no_todo",
    is_flag=True,
    default=False,
    help="期限の近い ToDo を出さない",
)
@click.option(
    "--days",
    "days",
    type=click.IntRange(min=1),
    default=1,
    help="対象の日を含めて何日ぶんの予定を出すか, default=1",
)
@click.option(
    "--memo",
    "memo",
    type=str,
    default=None,
    help="メッセージの先頭に出す文言",
)
@click_common_opts(__version__)
def notify(ctx, datadir, date_str, no_todo, days, memo, debug):
    """notify"""
    debug = _is_debug(ctx, debug)
    loggerInit(debug=debug)

    if date_str is None:
        date = datetime.date.today()
    else:
        date = datetime.date.fromisoformat(date_str)

    sd = SchedData(datadir)
    print(
        build_notify_text(
            sd, date, include_todo=not no_todo, days=days, memo=memo
        )
    )


if __name__ == "__main__":
    cli(prog_name=__prog_name__)
