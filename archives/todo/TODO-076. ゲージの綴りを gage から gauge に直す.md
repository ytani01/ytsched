# TODO-076. ゲージの綴りを `gage` から `gauge` に直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | verifier + wording |
| 実施 | Opus 5 / effort medium | verifier + wording |
| 消費 | output 11,327 / cache_creation 108,982 / 概算 $1.4 |
|      | main 81% + verifier 13% + wording 6%（料金の割合） |

## きっかけ

英語では gauge が正しい綴りで、gage は別の語。ゲージを入れた TODO-058
から一貫して誤った綴りを使っていた。

## やったこと

`src/` と `tests/` の 7 ファイルに
`sed 's/gage/gauge/g; s/Gage/Gauge/g; s/GAGE/GAUGE/g'` をかけた（110 か所）。
着手前に、既知の識別子以外の `gage` が無いことを grep で確かめてある。

- `src/ytsched/main_handler.py` — `GAUGE`・`DAYS_GAUGE_K`・
  `DAYS_GAUGE_MAX`・`calc_gauge_label()`
- `src/ytsched/webroot/static/js/my.js` — `dispGauge()`・
  `setGaugePosition()`・`gaugeBarClickHdr()`・`gaugeDiffLabel()`・
  `getGaugeMonday()` / `setGaugeMonday()`・`GAUGE_MONDAY_KEY`
- `src/ytsched/webroot/templates/main.html` — `#gauge_r`・
  `#gauge_r_label`・`.my-gauge-*`・`{{ gauge_label }}`
- `src/ytsched/webroot/static/css/my.css` — `.my-gauge-*`
- `tests/test_main_handler.py`・`test_web.py`・`test_browser.py` —
  テスト名と参照

`sessionStorage` のキーが `ytsched_gage_monday` から
`ytsched_gauge_monday` に変わる。既存セッションの「前の週」が一度だけ
失われ、針が中央から動き出すのが 1 回起きるだけなので、移行の手当ては
していない。

**`archives/` は直していない**（366 か所）。現行仕様ではない記録で、
当時のコードの綴りをそのまま残す。この TODO-076 より前の archives に
出てくる `gage` は、すべて現在の `gauge` と読み替えること。

## テスト

- `mise run lint` — `ruff check` / `basedpyright` / `mypy` すべて通過。
  `ruff format` が `tests/test_main_handler.py` を 1 か所整形した
  （`calc_gauge_label(...)` が 1 文字伸びて行の折り返しが変わったため）
- `uv run pytest -q` — 457 passed
- 一時ディレクトリを `--datadir` に指定して起動し、`curl` で HTTP 200。
  `#gauge_r` / `#gauge_r_label`（`±0`）/ `.my-gauge-label` が正しく
  展開されていること、テンプレートの生残りが無いことを確認

確認は verifier（`archives/agents/TODO-076/verifier-report.md`）、
`.md` の語は wording（同ディレクトリの `wording-report.md`）が見た。
