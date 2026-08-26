#
# (c) 2026 ytani01
#
"""TODO 項目ごとのトークン消費量を集計する (TODO-035)

Claude Code の transcript (``~/.claude/projects/<プロジェクト>/``) から、
TODO 項目ごとのトークン消費量を集計して表示する。

範囲は git のコミット時刻で切る。

* 始点 -- ``docs(todo):`` で始まり、``TODO-NNN`` を含むコミット
* 終点 -- ``docs(todo):`` 以外で、``（TODO-NNN）`` (全角カッコ) を
  含むコミット

# 使い方

```
uv run python tools/token-usage.py TODO-034
uv run python tools/token-usage.py TODO-034 --since '2026-08-23 14:00:00'
uv run python tools/token-usage.py --list
```

``mise run tokens -- TODO-034`` でも同じ。
"""

__author__ = "ytani01"
__date__ = "2026/08"

import argparse
import dataclasses
import datetime
import json
import pathlib
import re
import subprocess
import sys
import unicodedata
from collections.abc import Iterator
from typing import Any

from ytsched.mylog import exmsg, getLogger, loggerInit

_log = getLogger("token-usage")

#: transcript の置き場所 (この下にプロジェクトごとのディレクトリがある)
CLAUDE_PROJECTS_DIR = pathlib.Path.home() / ".claude" / "projects"

#: 始点にするコミットの接頭辞
START_PREFIX = "docs(todo):"

#: 担当名: 親セッション
MAIN_AGENT = "main"

#: 担当名: ``agent-*.meta.json`` が無いとき
UNKNOWN_AGENT = "unknown"

#: 単価 ($/1M トークン)。``message.model`` の前方一致で引く
#: (``claude-haiku-4-5-20251001`` のように日付が付くことがあるため)。
#: **Sonnet 5 の $2/$10 は 2026-08-31 までの導入価格。そのあとは
#: $3/$15 になるので書き換えが要る。**
PRICING: dict[str, tuple[float, float]] = {
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

#: 表に無いモデルを数えるときの既定 (多めに見積もる側に倒す)
DEFAULT_PRICING_MODEL = "claude-opus-5"

#: cache write (``cache_creation``) は input の何倍で概算するか
CACHE_WRITE_MULTIPLIER = 1.25

#: cache read (``cache_read``) は input の何倍で概算するか
CACHE_READ_MULTIPLIER = 0.1

#: ``git log --pretty=format:`` の区切り (本文に現れない制御文字)
SEP_FIELD = "\x1f"
SEP_RECORD = "\x1e"

#: 引数に受ける TODO 番号 (``TODO-034`` / ``034`` / ``34``)
TODO_ARG_PATTERN = re.compile(r"\A(?:TODO-)?([0-9]{1,4})\Z", re.IGNORECASE)

#: コミットメッセージから TODO 番号を拾う
TODO_MSG_PATTERN = re.compile(r"TODO-([0-9]{3})(?![0-9])")


def normalize_todo(arg: str) -> str:
    """``34`` ``034`` ``TODO-34`` を ``TODO-034`` に揃える。

    Raises
    ------
    ValueError
        TODO 番号として読めない場合

    """
    match = TODO_ARG_PATTERN.match(arg.strip())
    if not match:
        raise ValueError(f"{arg!r}: invalid TODO number")

    return f"TODO-{int(match.group(1)):03d}"


def todo_pattern(todo: str) -> re.Pattern[str]:
    """``TODO-034`` にだけ当たる正規表現 (``TODO-0341`` には当てない)。"""
    return re.compile(re.escape(todo) + r"(?![0-9])")


def project_dir(cwd: pathlib.Path | None = None) -> pathlib.Path:
    """カレントディレクトリから transcript のディレクトリを決める。

    Claude Code は ``/home/ytani/work/ytsched`` を
    ``-home-ytani-work-ytsched`` という名前にして
    ``~/.claude/projects/`` の下に置く。

    Raises
    ------
    FileNotFoundError
        そのディレクトリが無い場合

    """
    if cwd is None:
        cwd = pathlib.Path.cwd()

    name = str(cwd.resolve()).replace("/", "-")
    path = CLAUDE_PROJECTS_DIR / name

    if not path.is_dir():
        raise FileNotFoundError(
            f"{path}: no transcript .. プロジェクトのトップで実行してください"
        )

    _log.debug(f"project_dir={path}")
    return path


@dataclasses.dataclass
class Commit:
    """``git log`` の 1 コミット"""

    hash: str
    """短縮ハッシュ"""

    date: datetime.datetime
    """author date (aware)"""

    subject: str
    """1 行目"""

    body: str
    """2 行目以降"""

    def __str__(self) -> str:
        return f"{self.hash} {self.subject}"


def git_log() -> list[Commit]:
    """コミットを新しい順に返す。"""
    fmt = SEP_FIELD.join(("%h", "%aI", "%s", "%b")) + SEP_RECORD

    result = subprocess.run(
        ["git", "log", f"--pretty=format:{fmt}"],
        capture_output=True,
        text=True,
        check=True,
    )

    commits: list[Commit] = []
    for record in result.stdout.split(SEP_RECORD):
        record = record.strip("\n")
        if not record:
            continue

        hash_, date_str, subject, body = record.split(SEP_FIELD)
        commits.append(
            Commit(
                hash=hash_,
                date=datetime.datetime.fromisoformat(date_str),
                subject=subject,
                body=body,
            )
        )

    _log.debug(f"commits={len(commits)}")
    return commits


def find_start(commits: list[Commit], todo: str) -> Commit | None:
    """項目を立てたコミット (``docs(todo):``) を探す。

    **1 行目だけを見る。** 本文には別の項目の番号も出てくる
    (``docs(todo): … TODO-034 …`` の本文に ``TODO-029`` があった)。

    **当てはまるものが複数あれば、いちばん古いものを返す。** 今の規約の
    前は決着も ``docs(todo):`` で書いていたので (TODO-013・TODO-022)、
    新しい順に見て最初に当たったものを返すと、決着のコミットを始点に
    してしまう (TODO-035 で verifier が見つけた)。
    """
    pattern = todo_pattern(todo)
    found: Commit | None = None

    # commits は新しい順。最後に当たったものがいちばん古い。
    for commit in commits:
        if not commit.subject.startswith(START_PREFIX):
            continue
        if pattern.search(commit.subject):
            found = commit

    return found


def find_end(commits: list[Commit], todo: str) -> Commit | None:
    """項目を済ませたコミット (``（TODO-NNN）``) を探す。

    始点と同じく 1 行目だけを見る。
    """
    mark = f"（{todo}）"

    for commit in commits:
        if commit.subject.startswith(START_PREFIX):
            continue
        if mark in commit.subject:
            return commit

    return None


def find_end_after(
    commits: list[Commit], todo: str, start: datetime.datetime
) -> Commit | None:
    """``start`` より後の終点を探す。無ければ None (まだ完了していない)。

    始点より前の終点は、同じ番号で立て直した項目の古いほうを指して
    いるので使わない。
    """
    end_commit = find_end(commits, todo)

    if end_commit and end_commit.date <= start:
        _log.warning(f"{end_commit}: older than start .. ignored")
        return None

    return end_commit


def parse_since(since: str) -> datetime.datetime:
    """``--since`` の文字列を aware な datetime にする。

    タイムゾーンが書かれていなければ、手元のローカル時刻とみなす。

    Raises
    ------
    ValueError
        日時として読めない場合

    """
    dt = datetime.datetime.fromisoformat(since.strip())
    if dt.tzinfo is None:
        dt = dt.astimezone()

    return dt


@dataclasses.dataclass
class Usage:
    """トークン消費量の合計"""

    output: int = 0
    """出力 (主指標)"""

    cache_creation: int = 0
    """キャッシュ書き込み (主指標)"""

    cache_read: int = 0
    """キャッシュ読み出し (表には出すが、消費の行には書かない)"""

    input: int = 0
    """キャッシュに載らなかった入力 (表には出さない)"""

    messages: int = 0
    """数えたメッセージ数"""

    cost: float = 0.0
    """概算料金 (ドル)"""

    def add(self, other: Usage) -> None:
        """足し込む。"""
        self.output += other.output
        self.cache_creation += other.cache_creation
        self.cache_read += other.cache_read
        self.input += other.input
        self.messages += other.messages
        self.cost += other.cost


@dataclasses.dataclass
class Record:
    """transcript の 1 行 (``message.usage`` を持つもの)"""

    timestamp: datetime.datetime
    agent: str
    model: str
    key: tuple[str, str]
    """重複を除くための ``(requestId, message.id)``"""

    usage: Usage


#: 単価表に無いモデル名を、警告済みとして覚えておく (何度も出さないため)
_warned_models: set[str] = set()


def price_for(model: str) -> tuple[float, float]:
    """``(input, output)`` の単価 ($/1M トークン) を前方一致で引く。

    **いちばん長く一致したものを採る。** ``claude-opus-4`` と
    ``claude-opus-4-5`` のように前方が重なる名前を ``PRICING`` に足した
    とき、書いた順で先に当たったほうが勝つのを避けるため。

    表に無いモデル名に当たったら警告を出し、``DEFAULT_PRICING_MODEL``
    (Opus 5) の単価で数える (多めに見積もる側に倒す)。
    """
    matched = [name for name in PRICING if model.startswith(name)]
    if matched:
        return PRICING[max(matched, key=len)]

    if model not in _warned_models:
        _warned_models.add(model)
        _log.warning(
            f"{model}: 単価表に無いモデル .. {DEFAULT_PRICING_MODEL} の単価で概算"
        )

    return PRICING[DEFAULT_PRICING_MODEL]


def record_cost(record: Record) -> float:
    """1 件の usage から概算料金 (ドル) を出す。"""
    input_price, output_price = price_for(record.model)
    usage = record.usage

    return (
        usage.output * output_price
        + usage.input * input_price
        + usage.cache_creation * input_price * CACHE_WRITE_MULTIPLIER
        + usage.cache_read * input_price * CACHE_READ_MULTIPLIER
    ) / 1_000_000


def agent_name(path: pathlib.Path) -> str:
    """``agent-*.jsonl`` の担当名を ``agent-*.meta.json`` から読む。"""
    meta_path = path.with_suffix(".meta.json")

    try:
        meta: dict[str, Any] = json.loads(meta_path.read_text())
    except (OSError, ValueError) as e:
        _log.warning(f"{meta_path}: {exmsg(e)} .. {UNKNOWN_AGENT}")
        return UNKNOWN_AGENT

    return str(meta.get("agentType") or UNKNOWN_AGENT)


def iter_transcripts(
    base: pathlib.Path,
) -> Iterator[tuple[str, pathlib.Path]]:
    """``(担当名, transcript のパス)`` を返す。

    親セッションは直下の ``<uuid>.jsonl``、サブエージェントは
    ``<uuid>/subagents/agent-*.jsonl``。
    """
    for path in sorted(base.glob("*.jsonl")):
        yield (MAIN_AGENT, path)

    for path in sorted(base.glob("*/subagents/agent-*.jsonl")):
        yield (agent_name(path), path)


def parse_line(line: str, agent: str) -> Record | None:
    """transcript の 1 行を ``Record`` にする。usage が無ければ None。"""
    try:
        data: dict[str, Any] = json.loads(line)
    except ValueError:
        return None

    message = data.get("message")
    if not isinstance(message, dict):
        return None

    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None

    timestamp = data.get("timestamp")
    if not isinstance(timestamp, str):
        return None

    return Record(
        timestamp=datetime.datetime.fromisoformat(timestamp),
        agent=agent,
        model=str(message.get("model") or "unknown"),
        key=(str(data.get("requestId")), str(message.get("id"))),
        usage=Usage(
            output=int(usage.get("output_tokens") or 0),
            cache_creation=int(usage.get("cache_creation_input_tokens") or 0),
            cache_read=int(usage.get("cache_read_input_tokens") or 0),
            input=int(usage.get("input_tokens") or 0),
            messages=1,
        ),
    )


def collect(
    base: pathlib.Path,
    start: datetime.datetime,
    end: datetime.datetime,
) -> list[Record]:
    """範囲内の ``Record`` を集める。

    **同じ usage が複数の行に現れる。**``(requestId, message.id)`` の
    組ごとに、各項目 (``output`` / ``cache_creation`` / ``cache_read`` /
    ``input``) の最大値を採る。サブエージェントの transcript には
    途中経過と最終値の両方が記録されていて、行の並びが最終値を後に
    置くとは限らないため、上書きではなく最大値で数える。``messages``
    は 1 のまま (リクエスト 1 件として数える)。
    """
    merged: dict[tuple[str, str], Record] = {}
    n_line = 0

    for agent, path in iter_transcripts(base):
        with path.open(encoding="utf-8") as f:
            for line in f:
                record = parse_line(line, agent)
                if record is None:
                    continue
                if not start <= record.timestamp <= end:
                    continue

                n_line += 1
                existing = merged.get(record.key)
                if existing is None:
                    merged[record.key] = record
                    continue

                existing.usage.output = max(
                    existing.usage.output, record.usage.output
                )
                existing.usage.cache_creation = max(
                    existing.usage.cache_creation, record.usage.cache_creation
                )
                existing.usage.cache_read = max(
                    existing.usage.cache_read, record.usage.cache_read
                )
                existing.usage.input = max(
                    existing.usage.input, record.usage.input
                )

    records = list(merged.values())
    for record in records:
        record.usage.cost = record_cost(record)

    _log.debug(f"lines={n_line}, uniq={len(records)}")
    return records


def sum_by(records: list[Record], key: str) -> dict[str, Usage]:
    """``agent`` か ``model`` ごとに合計する (料金の多い順)。"""
    total: dict[str, Usage] = {}

    for record in records:
        name = str(getattr(record, key))
        total.setdefault(name, Usage()).add(record.usage)

    return dict(
        sorted(total.items(), key=lambda kv: kv[1].cost, reverse=True)
    )


def total_of(records: list[Record]) -> Usage:
    """全体の合計。"""
    total = Usage()
    for record in records:
        total.add(record.usage)

    return total


def fmt_time(dt: datetime.datetime) -> str:
    """ローカル時刻の文字列にする。"""
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


def disp_width(text: str) -> int:
    """端末での表示幅 (全角は 2 と数える)。"""
    return sum(
        2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text
    )


def pad(text: str, width: int) -> str:
    """表示幅で左詰めにする。"""
    return text + " " * max(width - disp_width(text), 0)


def print_table(title: str, table: dict[str, Usage], total: Usage) -> None:
    """内訳の表を出す。"""
    names = [*table, title, "合計"]
    width = max([disp_width(name) for name in names] + [12])

    print()
    print(
        f"{pad(title, width)} {'output':>10} {'cache_creation':>15}"
        f" {'(cache_read)':>15} {'msgs':>6} {'$':>10}"
    )
    for name, usage in [*table.items(), ("合計", total)]:
        print(
            f"{pad(name, width)} {usage.output:>10,}"
            f" {usage.cache_creation:>15,} {usage.cache_read:>15,}"
            f" {usage.messages:>6,} {'$' + format(usage.cost, ',.1f'):>10}"
        )


def fmt_shares(by_agent: dict[str, Usage], total: Usage) -> str:
    """``main 40% + implementer 35%`` の形にする (料金の割合)。"""
    if total.cost <= 0:
        return ""

    return " + ".join(
        f"{name} {round(usage.cost * 100 / total.cost)}%"
        for name, usage in by_agent.items()
    )


def print_summary(by_agent: dict[str, Usage], total: Usage) -> None:
    """archives の TODO ファイルへ貼る形で出す。"""
    print()
    print(
        f"消費: output {total.output:,}"
        f" / cache_creation {total.cache_creation:,}"
        f" / 概算 ${total.cost:,.1f}"
    )
    print(f"      {fmt_shares(by_agent, total)}（料金の割合）")
    print(
        f"（参考: cache_read {total.cache_read:,}"
        f"、メッセージ {total.messages:,} 件）"
    )


def print_range(
    todo: str,
    start: datetime.datetime,
    end: datetime.datetime,
    start_commit: Commit | None,
    end_commit: Commit | None,
) -> None:
    """集計した範囲を出す。"""
    start_src = str(start_commit) if start_commit else "--since"
    print(f"{todo} の範囲")
    print(f"  始点 {fmt_time(start)}  {start_src}")

    if end_commit:
        print(f"  終点 {fmt_time(end)}  {end_commit}")
    else:
        print(f"  終点 {fmt_time(end)}  (まだ完了していない: 現在時刻まで)")


def show(todo: str, since: str | None) -> int:
    """1 項目を集計して表示する。返り値は終了コード。"""
    # 先に transcript のありかを確かめる (何か出す前に落とすため)
    base = project_dir()
    commits = git_log()

    start_commit = None if since else find_start(commits, todo)
    if since:
        start = parse_since(since)
    elif start_commit:
        start = start_commit.date
    else:
        print(
            f"{todo}: 始点のコミット"
            f"（`{START_PREFIX} … {todo} …`）が見つかりません。"
            " --since で始点を指定してください。",
            file=sys.stderr,
        )
        return 1

    end_commit = find_end_after(commits, todo, start)
    if end_commit:
        end = end_commit.date
    else:
        end = datetime.datetime.now().astimezone()

    print_range(todo, start, end, start_commit, end_commit)

    records = collect(base, start, end)
    if not records:
        print("\nこの範囲の transcript がありません。", file=sys.stderr)
        return 1

    total = total_of(records)
    by_agent = sum_by(records, "agent")

    print_table("担当", by_agent, total)
    print_table("モデル", sum_by(records, "model"), total)
    print_summary(by_agent, total)

    return 0


def show_list() -> int:
    """集計できる項目を新しい順に一覧する。"""
    commits = git_log()

    print(f"{'TODO':<10} {pad('始点', 20)} {pad('終点', 20)}")

    # 始点は find_start() と同じで、同じ番号が複数あればいちばん古いもの。
    # commits は新しい順なので、当たるたびに上書きすれば最後に残るのが
    # いちばん古い。dict は入れた順を保つので、並びは新しい順のまま。
    starts: dict[str, Commit] = {}
    for commit in commits:
        if not commit.subject.startswith(START_PREFIX):
            continue

        for num in TODO_MSG_PATTERN.findall(commit.subject):
            starts[f"TODO-{num}"] = commit

    for todo, commit in starts.items():
        end_commit = find_end_after(commits, todo, commit.date)
        end_str = fmt_time(end_commit.date) if end_commit else "(未完了)"
        print(
            f"{todo:<10} {pad(fmt_time(commit.date), 20)} {pad(end_str, 20)}"
        )

    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """コマンドライン引数を解釈する。"""
    parser = argparse.ArgumentParser(
        description="TODO 項目ごとのトークン消費量を集計する"
    )
    parser.add_argument(
        "todo",
        nargs="?",
        help="TODO 番号 (TODO-034 / 034 / 34)",
    )
    parser.add_argument(
        "--since",
        help="始点の時刻 ('2026-08-23 14:00:00')。指定すると始点は探さない",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_",
        help="集計できる項目を一覧する",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="デバッグ出力"
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """エントリポイント。"""
    args = parse_args(argv)
    loggerInit(debug=args.debug)

    try:
        if args.list_:
            return show_list()

        if not args.todo:
            print("TODO 番号を指定してください（--help）。", file=sys.stderr)
            return 1

        return show(normalize_todo(args.todo), args.since)

    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print(exmsg(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
