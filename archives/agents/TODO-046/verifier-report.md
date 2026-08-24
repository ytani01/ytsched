# TODO-046 verifier 報告

## 1. lint / test

- `mise run lint` → fmt（ruff format 24 files left unchanged / ruff check All
  checks passed）、typecheck（basedpyright 0 errors 0 warnings 0 notes /
  mypy Success: no issues found in 21 source files）ともに ○
- `uv run pytest` → 418 passed（2.76s）○

## 2. `--help`

- `uv run --with playwright python tools/screenshot.py --help` → ○。
  引数一覧、既定値、末尾の epilog（`--datadir` に一時ディレクトリを指定する
  旨）まで表示された

## 3. 実際に撮る

- 一時データディレクトリ（scratchpad 配下）に `2026/08/24.jsonl` を作成し、
  `detail` に改行入りの 3 行（`議題\n・進捗確認\n・来月の予定`）を持つ
  「予定」を 1 件用意した
- `uv run ytsched webapp --datadir <一時dir> --port 10099` を起動 → `curl` で
  200 を確認
- `uv run --with playwright python tools/screenshot.py http://localhost:10099/
  --open -p todo046 -o <一時out>` を実行 → 4 枚（`closed_412` `open_412`
  `closed_800` `open_800`）を保存。標準出力にパスが 4 行出た
- `file` で全て `PNG image data`、`closed_412`/`open_412` は 412x900、
  `closed_800`/`open_800` は 800x900。サイズは 53〜57KB で壊れは無い
- `closed_412` と `open_412` を実際に開いて見比べた。closed では detail が
  1 行に省略され、open では 3 行とも展開されて表示されていた
  （`v`/`^` のアイコンも切り替わっている）。閉じた状態・開いた状態の
  両方が撮れることを確認 ○
- `mise run shot -- http://localhost:10099/ --open -p todo046b -o <一時out>`
  でも同じく 4 枚保存された（`docs/Developer.md` の手順どおり）○

## 4. 失敗時の振る舞い

- (a) アプリが動いていない URL（`http://localhost:19999/`）→
  `Error: Page.goto: net::ERR_CONNECTION_REFUSED ...` に続けて
  「アプリが http://localhost:19999/ で動いているか確かめる。」、
  終了ステータス 1 ○
- (b) `--chromium /usr/bin/no-such-chromium` →
  「ブラウザが見つからない: /usr/bin/no-such-chromium」「--chromium で
  場所を指定する。」、終了ステータス 1 ○

## 5. `docs/Developer.md` の手順の再現

- 「## 画面を撮る」節の `uv run ytsched webapp --datadir /tmp/x --port
  10085 &` → `mise run shot -- --open -p todo046` の型を、上記 3・4 で
  実際になぞって確認済み ○
- `mise run tokens -- TODO-046` も掲載例どおり実行でき、出力の書式
  （`消費:` 行）も既存の形式と合っていた ○

## 後片付け

- 起動した webapp（pid 367663 / 367667）は `pgrep -fa` で確認後 `kill`。
  停止を再確認した
- `~/ytsched/data` は触っていない。`~/tmp/playwright-mcp/` は今回の一時
  ファイルを置かず（`-o` で scratchpad 配下を指定）、既存ファイルのみで
  汚れていないことを確認した

## 見つかったこと

なし。挙動・メッセージ・終了ステータスとも依頼どおりで、コードの不具合は
見つからなかった。
