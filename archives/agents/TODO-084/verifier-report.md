# TODO-084 verifier 報告

## 1. `mise run fmt` / `typecheck` / `lint` / `test`

- `mise run fmt` — ○（`ruff format`: 30 files left unchanged、`ruff check`: All checks passed）
- `mise run typecheck` — ○（basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success: no issues found in 27 source files）
- `mise run lint` — ○（fmt + typecheck をまとめて実行、同じ結果）
- `mise run test`（`uv run pytest tests`） — ○ 482 件すべて通過（61.22s）

## 2. `tests/test_browser.py` の新規 3 本を、実装を戻して落ちることを確認

作業ツリーは汚さず、`/tmp/.../scratchpad/todo084-verify/ytsched` へ `cp -r` して確認した。
**注意点**: 最初 `cp -r` で `.venv` ごとコピーしたところ、`.venv/bin/pytest` の
shebang が `#!/home/ytani/work/ytsched/.venv/bin/python3`（コピー元の絶対パス）の
ままで、`uv run pytest` で実行したテストが**元のソース（未変更）を使って
走っていた**（`uv run python -c "import ytsched; print(__file__)"` では
コピー先を指すのに、`uv run pytest` は shebang 経由でコピー元の venv を
使っていた）。**このため最初の確認は無効だった。** `.venv` を消して
`uv sync` でコピー先に作り直してから、以下を確認した。

- `main-page.js` の `window.addEventListener('pointerup', pageTurnPointerUpHdr);`
  をコメントアウトして走らせると:
  - `test_double_tap_starts_auto_page_turn` — × タイムアウト（`playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 10000ms exceeded.`）
  - `test_tap_again_stops_auto_page_turn` — × 同上でタイムアウト
  - `test_swipe_from_button_does_not_move_a_week` — ○（この変更とは無関係なので通る。想定どおり）
- 上を元に戻し、`swipe.js` の `touchStartHdr()`/`mouseDownHdr()` の
  `closest()` から `, [data-page-turn]` を外すと:
  - `test_swipe_from_button_does_not_move_a_week` — ×
    `AssertionError: assert '2026-08-17' == '2026-08-24'`
    （ボタンの上からの払いで週が動いてしまう）

3 本とも、対応する実装を戻すと想定どおり落ちることを確認した。
確認後、一時ディレクトリは削除済み。作業ツリー（`/home/ytani/work/ytsched`）は
`git status --short` で元の diff のみに戻っていることを確認した。

## 3. アプリの起動と `conf.json` の `AutoTurnMsec`

`--datadir` に一時ディレクトリを指定して起動（`--port 18101`）。

- `conf.json` 無し — ○ `const auto_turn_msec = 700;`
- `{"AutoTurnMsec": "1234"}` — ○ `const auto_turn_msec = 1234;`
- `{"AutoTurnMsec": 1234}`（数値、文字列でない） — ○ 700 に落ち、
  警告 1 行: `'AutoTurnMsec'=1234: not a string .. ignored`
- `{"AutoTurnMsec": "99999"}`（範囲の外） — ○ 700 に落ち、
  警告 1 行: `AutoTurnMsec='99999': AutoTurnMsec must be in 300..10000, not 99999 .. ignored`
- `{"AutoTurnMsec": "abc"}`（数字でない） — ○ 700 に落ち、
  警告 1 行: `AutoTurnMsec='abc': invalid literal for int() with base 10: 'abc' .. ignored`
- `{"AutoTurnMsec": "100"}`（範囲の外・下限未満） — ○ 700 に落ち、
  警告 1 行: `AutoTurnMsec='100': AutoTurnMsec must be in 300..10000, not 100 .. ignored`
- どのケースでも `conf.json` の中身は書き換わっていない（`cat` で確認）
- サーバのログに例外・トレースバックは出ていない

## 4. ダブルタップでの自動ページ送り（既定値 700）

playwright を直に使い、`#forward_button` を `pointerdown`→`pointerup`
（`page.mouse`）で 2 回連続してタップした。

- ダブルタップ後、`page.wait_for_function()` で 3 週先まで自動的に
  進むことを確認（`moveToMonday` が繰り返し呼ばれている）
- その次のタップで停止し、以後 2100ms（≒ 700ms の 3 倍）待っても
  `data-monday` が変わらないことを確認

（補足）Python 側の往復（`bounding_box()` 呼び出しなど）に時間がかかる
書き方で確かめると、「停止直前に読んだ週」と「停止直後に読んだ週」の
間に 1〜2 週分のずれが出ることがあった。これは `wait_for_timeout()` の
間もタイマーが実時間で動き続けるための見かけ上のもので、`wait_for_function`
を使った確認では問題なく、**停止した後は狙いどおり動きが止まる**ことを
確認できた。

## 気づいたが直さなかったもの

なし。挙動・表示とも依頼どおりだった。
