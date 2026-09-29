# TODO-208 reviewer の報告

対象: 未コミットの `git diff`（`src/ytsched/trash.py`、`tests/test_trash.py`、
`tests/test_web.py`、`docs/data-format.md`、`src/README.md`）

## 結論

確信度の高い指摘は無し。

## 見たこと

### 1. 分岐・例外の捕捉

- `entries()` / `delete_many()` の `except` には、変更前から `ValueError` が
  入っている。`UnicodeDecodeError` は `ValueError` のサブクラスなので、
  デコードを `try` の中へ移しただけで捕まる。`count()` には `ValueError` が
  無かったので足してある。3 つとも漏れは無い
- `count()` に `ValueError` を足したことで新しく捕まるのは、実質的に
  `UnicodeDecodeError` だけ（`JSONDecodeError` は元から捕まえており、
  `data["trashed_at"]` から `ValueError` は出ない）。意味は変わっていない
- 呼び出し側（`rg -n "trash|TrashFile" src`）: `main_handler.py:83` の
  `count()`、`trash_handler.py` の `entries()` / `get()` / `max_version()` /
  `delete_many()`。`get()` と `max_version()` は `entries()` を通るので
  ここで一緒に直っている。`SchedData.max_version()`（`ytsched.py:1191`）と
  `fix_id.py` は元からバイトで読み `UnicodeDecodeError` を捕まえている
- 行の切り方は `\n` だけになり、`SchedDataFile.split_lines()` と同じ
- BOM: 変更前も変更後も `utf-8`（`utf-8-sig` ではない）なので、先頭の BOM は
  どちらも `﻿` として残り、`json.loads()` が `JSONDecodeError` を出して
  その行を飛ばす。差は無い
- CRLF: 変更前はテキストモードで `\n` に直して読み、`delete_many()` の書き直しで
  `\n` に変えていた。変更後は `\r\n` のまま読んで `json.loads()` が空白として
  受け、書き直しでも `\r\n` のまま残る。どちらも読めるので、実害は無い
- `_write_lines()` は `"wb"` にしてあり、`kept` は元のバイトのまま書き戻す。
  一時ファイル経由で差し替える流れは変わっていない

### 2. 新規テストは壊すと落ちるか

`git stash push src/ytsched/trash.py` で `trash.py` だけ変更前に戻して、
`pytest -k undecodable tests/test_trash.py tests/test_web.py` を実行した
（実行後に `git stash pop` で戻し、`git diff --stat` が元の 5 ファイルと
同じであることを確かめた）。

| | 変更後 | 変更前の `trash.py` |
|---|---|---|
| `test_undecodable_bytes_are_skipped` | pass | FAIL（UnicodeDecodeError） |
| `test_delete_many_keeps_undecodable_line_as_is` | pass | FAIL（UnicodeDecodeError） |
| `TestTrashHandler::test_undecodable_bytes_do_not_break_pages` | pass | FAIL（`GET /ytsched/` が 500） |

コードを読んだかぎりでは、3 つのメソッドのどれか 1 つだけを戻しても、
どれかのテストが落ちる。

- `count()` だけ戻す → 両方のテストの先頭の `count()`、web の `/`
- `entries()` だけ戻す → `test_undecodable_bytes_are_skipped` の `entries()`
- `delete_many()` をテキストモードに戻すか、`errors="replace"` などで直して書く
  → `read_bytes() == bad` / `endswith(bad)` で落ちる

壊れた行を有効な行の間に挟んでいるので、「壊れた行で読むのを止める」
実装も `count() == 2` で落ちる。

### 3. 文書と実装

- `docs/data-format.md`: 「バイトで読んで行ごとにデコード」「利用できない行だけ
  警告して飛ばす」「`count()` に入れない」「`delete_many()` は元のバイトの
  まま残す」は実装と合っている
- `trash.py` の `delete_many()` の docstring も合っている

## 確信度が低いもの

- **`src/README.md` の「デコードできない行だけを飛ばす」**（追記の 1 行目）:
  実際には JSON として読めない行なども飛ばしている。「（ファイル全体ではなく）
  その行だけ」の意味なら正しいが、「飛ばすのはデコードできない行だけ」とも
  読める。`docs/data-format.md` の書き方（「利用できない行（…、など）だけ」）
  のほうが誤解が無い。言い回しの問題で、実害は未確認
- **`\r` だけで区切られたファイル**: 変更前のテキストモード（`newline=None`）は
  `\r` だけでも行を切っていた。変更後は `\n` でしか切らないので、そういう
  ファイルは全体が 1 行になり、全件飛ばされる（`delete_many()` はその 1 行を
  残すのでデータは消えない）。`append()` は `\n` で書き、`json.dumps()` は
  `\r` をエスケープするので、手で編集しないかぎり起きない。`SchedDataFile` と
  同じ振る舞いなので揃ったとも言える。境界線上の判断で、実害は未確認
