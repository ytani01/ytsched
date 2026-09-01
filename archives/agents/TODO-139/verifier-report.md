# TODO-139 verifier 報告

## 自動チェック

- `uv run pytest -q` → ○ 578 passed in 152.07s
- `uv run ruff format --check src/ tests/` → ○ 35 files already formatted
  （`ruff format --check` をリポジトリ全体に掛けると `archives/` 配下の
  既存 .md 9 件が unformatted と出るが、今回の変更対象外・既存の状態）
- `uv run ruff check` → ○ All checks passed!
- `uv run basedpyright` → ○ 0 errors, 0 warnings, 0 notes

## アプリを実際に動かした確認

一時ディレクトリ（`/tmp/.../scratchpad/data2`）を `--datadir` に指定して
`uv run ytsched webapp --datadir ... --port 18765` を起動し、`TrashFile.add()`
で `trash.jsonl` に手作業でエントリ（`aaa` 1 件、`bbb` を 2 回、壊れた
JSON 行 1 行）を仕込んで確認した。

- **1 件削除（同一 `sde_id` の巻き添え確認）**: `bbb` を 2 回削除して
  作った 2 行のうち、後から消した 1 行だけを `trashed_at` 指定で
  `cmd=delete` した。結果、`bbb` の残り 1 行・`aaa`・壊れた行は
  そのまま残った。○ 巻き添え無し
- **空にする（`cmd=clear`）**: 実行後 `trash.jsonl` は 0 バイトになり、
  壊れた行も含めて全消去された（`clear` は全消去なので仕様通り）。
  画面にも「ゴミ箱は空です」が出た。○
- **存在しない `trashed_at` の `delete`**: `HTTP/1.1 404 Not Found`。○
- **`?sde_id=` 絞り込み時に「空にする」が出ない**: `grep -c "空にする"` が
  0。○ 未絞り込み・3 件のときは表示された。○
- **0 件のとき**: 「空にする」ボタン出ず、「ゴミ箱は空です」が出た。○
- **redirect 先**: `delete` / `clear` とも `Location: /ytsched/trash`、
  302。○
- **`confirm()` のキャンセル**: `tests/test_browser.py` の fixture は
  流用せず、同等の手順（playwright + `/usr/bin/chromium`）を
  scratchpad のスクリプトで直接動かして確認した。`page.on("dialog", ...)`
  で `dismiss()` し、削除ボタンをクリックしても `.my-trash-entry` の
  件数が変わらず、URL も `/ytsched/trash` のまま（送信されていない）。
  ダイアログの文言も `data-confirm` の文字列と一致。○
- **テンプレートの生展開**: `curl` で取得した HTML に `{{` `{%` の
  残りは無し。○
- **サーバログ**: 一連の操作後、`error` / `traceback` / `exception` の
  出力は無し。○

## 見つけたこと（不具合）

- **`src/ytsched/trash.py` の `_write_lines()`（`delete()` / `clear()`
  経由）で、書き直し後に `trash.jsonl` のパーミッションが変わる。**
  実測: 事前に `chmod 644` した状態から `cmd=delete` を 1 回実行しただけで
  `0644` → `0600` になった（`cmd=clear` でも同様に再現）。
  `tempfile.mkstemp()` が 0600 でファイルを作り、`Path.replace()` で
  そのまま差し替えているため。`SchedDataFile` 側が同じパターンを
  どう扱っているかは見ていないが、既存の `trash.jsonl` が 0644 で
  運用されているなら、初回の削除操作でパーミッションが変わる。

他の確認項目はすべて期待どおりだった。

## 再確認（パーミッションの修正）

`_write_lines()` に `os.fchmod()` で元の `trash.jsonl` のパーミッションを
一時ファイルへ引き継ぐ処理が入った（`git diff src/ytsched/trash.py`）ので、
その 1 点だけ再確認した。アプリを別ポート（18766）・別の一時
`--datadir` で起動し、`chmod` で権限を変えてから `cmd=delete` /
`cmd=clear` を実際に叩いて `ls -la` で前後を比較した。

- 0644 → `cmd=delete` → 0644 のまま。○
- 0600 → `cmd=delete` → 0600 のまま。○
- 0640 → `cmd=clear` → 0640 のまま。○
- サーバログに例外・トレースバックは無し。○

自動チェック（再実行分のみ）:

- `uv run pytest tests/test_trash.py -q` → ○ 15 passed
- `uv run ruff check` → ○ All checks passed!
- `uv run ruff format --check src/ tests/` → ○ 35 files already formatted
- `uv run basedpyright` → ○ 0 errors, 0 warnings, 0 notes

パーミッションの不具合は解消を確認した。他の指摘は無し。

## 再確認（表示崩れの修正後）

`trash.html` / `my.css`（レイアウト）、削除日時を秒までに削る変更
（`entry.trashed_at.split('.')[0]`）が入った。`tests/test_browser.py` を
含む全件を再実行した。

- `uv run pytest`（全件） → ○ 579 passed in 152.04s（前回 578 件から
  1 件増。`test_browser.py` を含めブラウザテストも失敗無し）
- `uv run ruff check` → ○ All checks passed!
- `uv run ruff format --check src/ tests/` → ○ 35 files already formatted
- `uv run basedpyright` → ○ 0 errors, 0 warnings, 0 notes

依頼どおり、ゴミ箱画面の動作確認はやり直していない。指摘は無し。
