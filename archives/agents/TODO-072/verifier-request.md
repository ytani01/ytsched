# TODO-072 verifier への依頼

## 何を変えたか

ゲージの針の上に出るラベルの単位を、差の大きさで切り替えるようにした。

- 1 ヶ月に届かないうちは週数（`+3w`）
- 1 ヶ月から 1 年までは月数（`+1.2m`、小数点以下 1 桁）
- 1 年からは年数（`+1.2y`、小数点以下 1 桁）
- 今週は `±0`（変更なし）

1 年 = 365.25 日、1 ヶ月 = 365.25 / 12 = 30.4375 日。

変更したファイル:

- `src/ytsched/main_handler.py` — `calc_week_diff()` を `calc_gage_label()`
  に置き換えた。`calc_week_diff()` は render から使われなくなったので消した
- `src/ytsched/webroot/templates/main.html` — `week_diff` の書式指定を
  やめ、`{{ gage_label }}` を出すだけにした
- `src/ytsched/webroot/static/js/my.js` — `weekDiffLabel(weeks)` を
  `gageDiffLabel(days)` に置き換えた。定数 `DAYS_MONTH` を足した
- `tests/test_main_handler.py`、`tests/test_web.py` — テストを直した／足した

## 確かめてほしいこと

1. `mise run lint`（fmt + typecheck）と `uv run pytest tests` が通るか。
   **ブラウザテスト（`tests/test_browser.py`）も走らせること。**
   既存の `test_gage_label_moves_with_the_needle` は `+3w`（21 日）を
   見ており、新仕様でも週数のままのはずだが、実際に通るかを見てほしい
2. **サーバ側（Python）と JavaScript 側の出力が食い違わないか。**
   読み込んだ直後はサーバが埋め、あとは JavaScript が書き換えるので、
   食い違うと針が動く前後で文字が変わって見える。
   main では -30y〜+30y の全週（3201 通り）で一致することを確かめたが、
   独立に確かめ直してほしい
3. 境界の値が仕様どおりか。4 週（28 日）はまだ `+4w`、5 週（35 日）から
   `+1.1m`、52 週（364 日）は `+12.0m`、53 週（371 日）から `+1.0y`
4. 実際にアプリを起動して、離れた週を開いたときにラベルが月数・年数で
   出るか。**`--datadir` には必ず一時ディレクトリを指定すること**
5. `calc_week_diff` を消したことで壊れた参照が残っていないか（grep）

## 注意

- **コードは直さないこと。** 見つけたことは報告するだけにする
- `mise run upgradeproject` は走らせない
- `ruff format` を素で叩かない。`mise run fmt` を使う
  （`--line-length 78` が要る。素で叩いて無関係なファイルを 16 個
  整形してしまい、戻した）

## 報告

`archives/agents/TODO-072/verifier-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」を 5 行以内で。
