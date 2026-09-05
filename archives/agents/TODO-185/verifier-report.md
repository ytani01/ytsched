# TODO-185 verifier 報告

## 実行したコマンドと結果

- `mise run lint` — 成功（ruff format 差分なし、ruff check / eslint とも通過）
- `mise run typecheck` — 成功（basedpyright 0 errors、mypy: Success: no issues found in 40 source files）
- `uv run pytest tests/ --ignore=tests/test_browser.py -q` — 611 passed
- `uv run pytest tests/test_browser.py -q -k gauge` — 15 passed, 57 deselected
- `grep -n "1000\|1秒\|1 秒" src/ytsched/webroot/static/js/gauge.js` — 該当なし
  （ハードコードされた `1000`、「1 秒」の記述はいずれも残っていない）

## アプリの起動確認

一時ディレクトリ（`/tmp/.../scratchpad/ytsched-verify/datadir1`）を
`--datadir` に指定して `uv run ytsched webapp --port 18185` を起動。

1. `conf.json` が無い状態で起動
   - HTTP 200
   - `#main` に `data-gauge-follow-msec="500"` あり
   - 自動生成された `conf.json` に `"GaugeFollowMsec": "500"` が入っている
2. `conf.json` に `"GaugeFollowMsec": "1500"` を手で書いて再起動
   - HTTP 200、`data-gauge-follow-msec="1500"`
3. `conf.json` に `"GaugeFollowMsec": "50"`（範囲外）を書いて再起動
   - HTTP 200、`data-gauge-follow-msec="500"`（既定へ落ちる）

各起動のログ（`server1.log` 〜 `server3.log`）に traceback・exception の類いは無し。
起動したプロセスはすべて `kill` で終了させた。

## 見つかった問題

なし。依頼の確認項目はすべて期待どおりの結果だった。

## 判断が要る点

なし。implementer-report.md にある「`abc` も一緒にテストした」「`src/README.md`
377 行目付近の `auto_turn_msec` 一覧は範囲外」の 2 点は判断が要る点として
implementer 側の報告に既に書かれている（範囲外の依頼だったので verifier では
確認していない）。
