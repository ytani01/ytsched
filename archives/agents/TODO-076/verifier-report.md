# TODO-076 verifier 報告

## 1. lint / typecheck / test

- `mise run lint`: ○（`ruff format` が 1 file reformatted、`ruff check` は
  All checks passed、`basedpyright` 0 errors、`mypy` Success）
  - reformatted されたのは `tests/test_main_handler.py` の
    `calc_gauge_label(...)` の呼び出し 1 箇所（行が長くなったための折り返し）。
    綴りの置換とは無関係の整形のみ
- `uv run pytest -q`: ○ 457 passed

## 2. 直し漏れ・直しすぎ

- `grep -rni "gage" src/ tests/` → 0 件（残留なし）
- `git diff --stat`: `src/ytsched/main_handler.py`,
  `webroot/static/css/my.css`, `webroot/static/js/my.js`,
  `webroot/templates/main.html`, `tests/test_browser.py`,
  `tests/test_main_handler.py`, `tests/test_web.py` の 7 ファイルで、依頼で挙げた対象と一致
- CSS クラス（`.my-gauge-bar` 等）、HTML id（`#gauge_r` / `#gauge_r_label`）、
  Jinja 変数（`gauge_label` / `gauge`）、Python 定数（`GAUGE` /
  `DAYS_GAUGE_K` / `DAYS_GAUGE_MAX`）、JS 側（`DAYS_GAUGE_K` /
  `DAYS_GAUGE_MAX` / `gaugeDiffLabel` / `GAUGE_MONDAY_KEY`
  (`ytsched_gauge_monday`) / `getGaugeMonday` / `setGaugeMonday` /
  `dispGauge` / `gaugeBarClickHdr`）、テスト側の参照（`#gauge_r_label`,
  `.my-gauge-bar`, `.my-gauge-r-needle`, `test_gauge_label_*` など）を
  grep で突き合わせ、両側とも揃っていることを確認。片側だけ直って
  壊れている箇所は見つからなかった

## 3. 起動確認

- `uv run ytsched webapp --datadir <一時ディレクトリ> --port 18765` を
  バックグラウンドで起動 → `curl http://127.0.0.1:18765/` → HTTP 200
- 取得した HTML に `{{ ` `{% ` の生残りなし（0 件）
- `#gauge_r` / `#gauge_r_label`（内容 `±0`）/ `.my-gauge-label` などが
  正しく展開されて出力されている
- `webapp.log` に例外・トレースバックなし
- 確認後、プロセスを kill 済み（`pgrep -fa "ytsched webapp"` で残存なし）

## 結論

不具合は見つからなかった。`archives/` は意図通り未変更（`gage` のまま）。
