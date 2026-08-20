# TODO-021 verifier の報告

## 結論

**不具合は見つからなかった。** 実装は依頼どおり「挙動を変えないリファクタリング」に
なっていることを、テスト・型チェック・実際のリクエストで確認した。

## 1. テストと lint・型チェック

```sh
uv run ruff format --line-length 78 --diff src tests   # 差分なし（19 files already formatted）
uv run ruff check --extend-select I --diff src tests   # 差分なし
uv run basedpyright src tests                           # 0 errors, 0 warnings, 0 notes
uv run mypy src tests                                   # Success: no issues found in 18 source files
uv run pytest tests                                      # 330 passed in 1.97s
```

- ruff の 2 つとも**書き換え無し**（`--diff` の出力が空）。実際にファイルへ
  書き込む形（`--fix`）でも良かったが、diff が空だったので同義
- pytest は依頼どおり **330 passed**（`test_handler.py` 15 + `test_main_handler.py`
  39 を含む）

## 2. 既存テストが書き換えられていないこと（最重要項目）○

```sh
git diff --stat
```

```
 TODO.md                     |  12 +-
 src/ytsched/__main__.py     |   4 -
 src/ytsched/handler.py      |  27 +-
 src/ytsched/main_handler.py | 764 ++++++++++++++++++++++++++++++--------------
 src/ytsched/ytsched.py      |  57 ++--
 tests/test_handler.py       |  22 +-
 6 files changed, 597 insertions(+), 289 deletions(-)
```

`tests/` の差分は `tests/test_handler.py` への **1 件の追記のみ**
（`test_settings_are_read` を丸ごと追加、`import os` と `URL_PREFIX` の
import を足しただけ）で、**既存の行は 1 行も変わっていない**ことを
`git diff tests/test_handler.py` の全文で確認した（マイナス側の行が
1 行も無い）。`tests/test_main_handler.py` は新規ファイル（untracked）。
報告どおり。

## 3. アプリの起動と、リファクタリングで触った経路 ○

```sh
uv run ytsched webapp --datadir <一時dir> --port 18085
```

- 起動後 `curl http://localhost:18085/ytsched/` → **HTTP 200**。テンプレートは
  展開済み（`{{ }}` / `{%` の生残りなし、`grep -c '{{'` / `'{%'` とも 0）
- `filter_str=会議` → 200、`search_str=会議&search_n=1` → 200
- **不正な正規表現** `filter_str=[` → 200。サーバログに
  `PatternError:unterminated character set at position 0:'['` の
  WARNING（例外・トレースバックではない）。入力欄には `value="["` が
  そのまま残り、TODO-012 どおり条件を無視して全件表示になっていることを
  HTML で確認
- `year=2026&month=8&day=21` → 200
- `cmd=add` → `cmd=fix`（`orig_date` 込み）→ `cmd=del` の一連を実施し、
  `2026/08/21.jsonl` / `2026/08/22.jsonl` の中身が期待どおり動くことを確認
  （**最初 `orig_date` を付け忘れて 21.jsonl にデータが残った現象に遭遇したが、
  これは私のテスト側の作法ミス。`orig_date` を付け直したら正しく移動・削除
  された。実装の不具合ではない**）
- ToDo の追加（`sde_type=□`）→ 完了（`deadline_date` 等を付けて
  `sde_type` を空にする、**`orig_date` は付けない** — `sde.html` の
  テンプレートで ToDo は `orig_date = None` になる仕様どおり）を実施し、
  `ToDo.jsonl` から消え、当日（`fix_todo_done()` が today にする）のファイルへ
  `〆2026/08/25 09:00-10:00\nmemo` が付いた形で移っていることを確認
- サーバログ（`server.log`）に出た WARNING は上記の不正な正規表現によるものと
  `sde_id` 未指定の 400（こちらもテストで意図的に叩いたもの）だけ。
  **例外・トレースバックは出ていない**
- 確認後、`pgrep -f "bin/ytsched webapp"` で PID を確かめてから `kill`。
  停止後の `curl --max-time 2` は接続失敗（`000`）で、プロセスが確実に
  止まっていることを確認
  - 補足: `pgrep -f "ytsched webapp"` は、この文字列を含む自分自身の
    シェルコマンド行まで拾ってしまい自己マッチした（`ps -fp` で確認すると
    実体が無い）。`pgrep -f "bin/ytsched webapp"` にして回避した

## 4. `ytsched x_data1` ○（コマンド名は `x-data1`）

```sh
uv run ytsched x-data1 2026 8 21 --datadir <一時dir>
```

例外を出さずデータを出力し、`__main__.py:88 x_data1()> end` の INFO ログが
出た（`DataFileApp.end()` を消した後も `finally` の `_log.info("end")` は
残っている、という implementer の報告どおり）。

依頼文の `x_data1` はコマンド名ではなく（実際は `x-data1`）、こちらは依頼書き方の
揺れなので不具合としては報告しない。

## 気づいた点（不具合ではない）

- `git status` の unstaged 一覧に `TODO.md` の変更も含まれていた
  （`+12/-`）。TODO-021 の中身に関わる差分かは見ていないが、
  implementer2 の報告には「`tests/` と `TODO.md` は触っていない」とあるので、
  この `TODO.md` の差分がどこから来たかは main の側で確認したほうがよい
  （verifier としてはこの差分の中身を読んで判断すべきものではないため、
  事実だけ報告する）

## 使った一時ディレクトリ

`/tmp/claude-649/-home-ytani-work-ytsched/6c139baf-2380-467a-8c2f-93f0027becff/scratchpad/ytsched-data`
（`~/ytsched/data` の実データには一切触れていない）
