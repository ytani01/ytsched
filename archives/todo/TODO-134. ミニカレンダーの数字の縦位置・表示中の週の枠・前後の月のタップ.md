# TODO-134. ミニカレンダーの数字の縦位置・表示中の週の枠・前後の月のタップ

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Sonnet 5 | main + verifier |
| 消費 | output 32,925 / cache_creation 173,254 / 概算 $2.3 |
|      | main 70% + verifier 30%（料金の割合） |

## きっかけ

ミニカレンダーについて、利用者から次の 3 点の指摘があった。

- 日付の数字の縦位置が、印（ドット・四角）の有無で上下にずれる
- 表示中の週を背景色（白とグレー）で分けているが、見づらいので枠で
  示してほしい
- 前後の月の日付（例: 2026/06 表示における 2026/07/01）がタップ
  （クリック）に反応しない

## やったこと

`src/ytsched/webroot/templates/main.html` と
`src/ytsched/webroot/static/css/my.css` を直した。

- `.my-mini-cal-marks` に `min-height: 8px`（ドット・四角と同じ高さ）
  を足し、印の有無によらず領域を確保して数字の縦位置を揃えた
- 週の背景色による区別（`.my-mini-cal-day-cur-week`、白 vs
  `#F0F0F0`）をやめ、全セルの背景を白にした（土日祝の色は残す）。
  代わりにテンプレート側で `mc_week` ごとに、その行の月曜が表示中の
  週に含まれるかを見て `<tr>` に `my-mini-cal-week-cur` クラスを
  付け、CSS で行の外周に `2px solid #888` を掛けた。今日のセル
  （`2px solid #28F`）とは、セレクタの詳細度を揃えて後勝ちにすることで
  衝突を避け、青い枠が優先されるようにした
- 前後の月の埋めセルにも、`d.in_month` の判定を外して常に
  `data-action="scroll-date" data-date="..."` を付けた。
  `scrollToDate()` は表示外の日付なら読み直す実装なので、そのまま
  動く。文字色は `#CCC` から `#999` にして、押せることが分かる程度に
  濃くした。曜日の背景色（土日祝）は、引き続き `d.in_month` のときだけ
  付ける（前後の月の埋めセルには色を付けない、という元の方針は変えて
  いない）

既存のテスト `tests/test_web.py` の
`TestMonthMiniCal.test_out_of_month_day_is_not_clickable` は新仕様と
矛盾するので、`test_out_of_month_day_is_clickable` に書き換え、埋め
セルに `data-action`・`data-date` が付くことを確かめる内容にした。

## テスト

- `mise run lint`（fmt / ruff / basedpyright / mypy / eslint）が通る
- `uv run pytest tests`（556 件）が通る
- 一時ディレクトリ（実データ非汚染）でアプリを起動し、`mise run shot`
  で見た目を確認。印の有無で数字の縦位置が揃っていること、表示中の週
  （8/31〜9/6）が灰色の枠で囲まれ、今日（8/31）の青い枠と衝突せず
  両立していることを画像で確認した
- Playwright で前後の月の埋めセル（2026-09-03 など）をクリックし、
  `scrollToDate()` が呼ばれて URL が `?date=2026-09-03` に変わる
  ことを確認した

以上は main（実装）と verifier（別セッションでの確認）の両方で
それぞれ確かめた。verifier からの指摘は無かった。
