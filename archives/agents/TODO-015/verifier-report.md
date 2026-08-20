# TODO-015 verifier 報告

結論: 問題なし。ruff の書き換え・整形は動作を変えておらず、
lint・型チェック・テスト・アプリの起動確認とも全て通った。

## 1. `git diff` を読んで気づいたこと

対象ファイル: `pyproject.toml`, `src/ytsched/__main__.py`,
`src/ytsched/edit_handler.py`, `src/ytsched/handler.py`,
`src/ytsched/main_handler.py`, `src/ytsched/webapp.py`,
`src/ytsched/ytsched.py`, `tests/helpers.py`, `tests/test_web.py`,
`tests/test_ytsched.py`

全ファイルを `git diff` で目視した。動作を変える変更は見つからなかった。

- **UP031（printf → f-string）**: 全箇所、対応関係（`%s`→`{}`、
  `%02d`→`:02d`）と引数の順序が一致していることを確認した。
  - `ytsched.py` `get_sortkey()`（旧: 265-271 行 / 新: 268-272 行）:
    `"%02d%02d%02d %s" % (year, month, day, timestr)` →
    `f"{year:02d}{month:02d}{day:02d} {timestr}"`。
    `%02d` は「最小 2 桁」の指定で、4 桁の年でも切り詰めは起きない
    （`:02d` も同じ意味）ので結果は一致する。実際に
    `test_date2path` 等のテストが通ることでも裏付けられる
  - `__main__.py` の `help="... default='%s'" % (...)` →
    f-string、`main_handler.py` の締切文字列組み立て
    （`deadline_date` を介した 3 行の f-string）も、
    出力文字列の並び・区切り文字とも元のままだった
  - `webapp.py` / `helpers.py` の URL パターン
    `r"%s" % self.URL_PREFIX` → `rf"{self.URL_PREFIX}"` は、
    生成される文字列が同じ（`URL_PREFIX` 自体に正規表現の特殊文字は
    含まれない）ことを確認。実際に `/ytsched/`・`/ytsched/edit` への
    ルーティングが動くことも確認済み（下記 4.）
- **RUF012（`ClassVar`）**: `SchedDataEnt` / `SchedDataFile` は
  dataclass ではない（`grep` で `@dataclass` が無いことを確認）ので、
  `ClassVar[...]` は型ヒントに過ぎず実行時の挙動に影響しない。
  `mypy` / `basedpyright` とも 0 件でエラー無し
- **SIM102（main_handler.py 387-388 行付近）**: 入れ子の
  `if not search_mode: if date1 == today():` を
  `if not search_mode and date1 == today():` にまとめた変更は、
  短絡評価の有無に関わらず真理値表が一致する（等価な書き換え）
- **PERF402**: `for sde in todo_today_sde: out_sde.append(sde)` →
  `out_sde.extend(todo_today_sde)` は等価
- **PLC0206（`htmlstr2text()`）**: `for k in resub_tbl: ...
  resub_tbl[k]` → `for k, v in resub_tbl.items(): ... v` は等価。
  コメントアウト行の変数名も揃えてあり、実害は無い
- **SIM118（`get_keys()`）**: `.keys()` を外した書き換えも等価
- **C408（`__main__.py`）**: `dict(help_option_names=[...])` →
  `{"help_option_names": [...]}` は等価
- **EXE001（シェバン削除）**: `edit_handler.py` / `handler.py` /
  `main_handler.py` / `webapp.py` の 1 行目
  `#!/usr/bin/env python3` を削除。いずれも相対 import
  （`from .handler import ...` など）を使っており単体実行できない
  モジュールなので、シェバンを消しても実害は無い。実際に
  `uv run ytsched webapp ...` で起動できることを確認した
  （4. 参照）

## 2. lint・型チェック・テスト

```
$ uv run ruff check --extend-select I src tests
All checks passed!

$ uv run ruff check src tests
All checks passed!

$ uv run ruff format --line-length 78 --check src tests
14 files already formatted

$ uv run basedpyright src tests
0 errors, 0 warnings, 0 notes

$ uv run mypy src tests
Success: no issues found in 14 source files

$ uv run pytest tests -q
174 passed in 1.20s
```

## 3. `pyproject.toml` の `ignore` が isort を打ち消していないか

`tests/_tmp_isort_check.py` に import 順を乱したファイルを一時的に
作って確認し、確認後に削除した（`git status --short tests/` で
残っていないことを確認済み）。

```
$ cat tests/_tmp_isort_check.py
"""一時ファイル: TODO-015 の I001 確認用（確認後に削除する）。"""
import re
import os

$ uv run ruff check tests/_tmp_isort_check.py   # --extend-select I 無し
I001 [*] Import block is un-sorted or un-formatted
...
Found 3 errors.

$ uv run ruff check --extend-select I tests/_tmp_isort_check.py
（同じ I001 が出る）
```

**分かったこと（判断は要らないが記録）**: このリポジトリの
ruff 0.16.3 は、`--extend-select I` を付けなくても I001 が出る。
`--isolated`（設定ファイルを一切読まない状態）でも同じファイルで
I001 が出ることを別途確認したので、`pyproject.toml` の
`ignore = ["DTZ005", "DTZ011"]` のせいではなく、この ruff の版で
すでに `I` が既定の select に含まれているらしい。したがって
`mise.toml` の `--extend-select I` は（少なくともこの版では）
効果が重複しているが、`ignore` が isort を打ち消しているという
懸念は該当しない＝**問題なし**。

## 4. アプリの起動確認

一時ディレクトリ（`mktemp -d`、例 `/tmp/tmp.sbDxwddOwG`）、
ポート 10287 で起動。

```
$ uv run ytsched webapp --datadir "$TMPDATA" --port 10287 &
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:10287/ytsched/
200
$ curl ... /ytsched/edit?date=2021-03-01
200
$ curl ... "/ytsched/?filter_str=test"
200
```

- 一覧画面・編集画面とも `{{ }}` `{%` が生で残っていないことを
  HTML を取得して確認（`grep -c "{{"` / `grep -c "{%"` とも 0）
- POST で予定を追加（`cmd=add`）→ 200。保存されたファイルを
  `cat -A` で見ると、タブ区切り（`^I`）のままだった:
  ```
  577480b7-...^I2021/03/01^I09:00-10:00^I^I検証テスト（EUC 表示は
  cat -A の都合。実データは UTF-8）^I会議室^Iverifier check$
  ```
- 検索（`search_str=検証`）で追加した予定がヒットすることを確認
  （一覧画面の本文に「検証」が含まれる）
- `Conf.cgi` もタブ区切り（`FilterStr^Itest$` など）のままだった
- サーバのログ（`server.log`）に例外・トレースバックは無し。
  出ていたのは意図的に送った不正な POST（`sde_id` 抜き）に対する
  `400 Missing argument sde_id` のみで、想定どおりの動き
- 確認後、`pgrep -f "ytsched webapp"` で実プロセス（python 側の
  PID）を確かめて `kill` した。一時ディレクトリも `\rm -rf` で
  削除した

## 見つかった不具合

無し。

## 追加確認（URL パターンの簡略化）

管理者が利用者の判断で以下 2 行を変更した後の再確認。

- `src/ytsched/webapp.py:95` — `(rf"{self.URL_PREFIX}", MainHandler)` →
  `(self.URL_PREFIX, MainHandler)`
- `tests/helpers.py:38` — `(rf"{URL_PREFIX}", MainHandler)` →
  `(URL_PREFIX, MainHandler)`

結論: 問題なし。ルーティングの挙動は変わっていない。

### 1. tornado のルーティング（`$` の自動付与）

`rf"{self.URL_PREFIX}"` と `self.URL_PREFIX` は、どちらも
`self.URL_PREFIX` の値がそのまま文字列になる（f-string の中身が
プレースホルダのみで、前後に固定文字列を足していないため）。
つまり生成される文字列は完全に同一で、tornado 側に渡る正規表現
パターンも変わらない。

念のため、tornado が付け足す `$` の扱いを Python の `re` で
確認した:

```
$ uv run python3 -c '
import re
p = re.compile(r"/ytsched" + "$")
print(p.fullmatch("/ytsched"))   # -> Match
print(p.fullmatch("/ytsched/"))  # -> None
'
```

末尾スラッシュ無しにはマッチし、末尾スラッシュ付きにはマッチしない
（別パターン `rf"{self.URL_PREFIX}/"` が担当する）という従来どおりの
住み分けが保たれていることを確認した。

### 2. lint・型チェック・テスト

```
$ uv run ruff check --extend-select I src tests
All checks passed!

$ uv run ruff format --line-length 78 --check src tests
14 files already formatted

$ uv run basedpyright src tests
0 errors, 0 warnings, 0 notes

$ uv run mypy src tests
Success: no issues found in 14 source files

$ uv run pytest tests -q
174 passed in 1.26s
```

### 3. アプリの起動確認

一時ディレクトリ（`mktemp -d`、`/tmp/tmp.Y0Bt8xi2SN`、確認後に
`\rm -rf` で削除済み）、ポート 10288 で起動。`~/ytsched/data` は
触っていない。

```
$ uv run ytsched webapp --datadir "$TMPDATA" --port 10288 &
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:10288/ytsched
200
$ curl -s -o /dev/null -w "%{http_code}" http://localhost:10288/ytsched/
200
```

- 末尾スラッシュ無し・有りとも 200 で、従来どおり両方とも
  `MainHandler` に届いていることを確認した
- サーバのログに例外・トレースバックは無し（起動ログのみ）
- `pgrep -f "ytsched webapp"` でプロセスを確かめて kill した

## 見つかった不具合（追加確認分）

無し。
