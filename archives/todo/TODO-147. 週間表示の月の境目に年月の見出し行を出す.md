# TODO-147. 週間表示の月の境目に年月の見出し行を出す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort high | main のみ + verifier |
| 消費 | output 25,565 / cache_creation 111,011 / 概算 $2.4 |
|      | main 82% + verifier 18%（料金の割合） |

## きっかけ

週間表示では、各日付ブロックの左端に「年 / 月 / 日 / 曜日 / 今日からの
日数」が縦に並んでいて、同じ年月が 7 日ぶん繰り返し出ていた。月の境目が
分かりにくく、日付欄も縦に詰まっていた。

年月を「YYYY/MM」の見出し行へ移し、日付欄は日・曜日・今日からの日数
だけにする。

決めたことは 3 つ。

- 見出し行は**各週の先頭に必ず出し、週の途中で月が替わればそこにも出す**。
  月をまたがない週にも出るので、どの週を見ても年月が分かる
- 週間表示の日付欄からは**年月とも消す**
- **検索モードは今までどおり**（日付欄に年月、年が替わるところに年）。
  検索結果は日付が飛び飛びで「週の先頭」が無く、見出し行では年月を
  追えないため

## やったこと

- `src/ytsched/webroot/templates/main.html`
  - 週パネルの先頭で `{% set cur_ym = '' %}` を置き、週ごとに状態を戻す。
    これで、月をまたがない週でも先頭で必ず 1 回は見出し行が出る
  - 検索モードでないとき、その日の `%Y/%m` が `cur_ym` と違えば
    `<div class="my-month-header">` を出して `cur_ym` を更新する。
    検索モード用の「年が替わったら年を出す」分岐の `{% else %}` に置いた
  - 日付欄の `my-date-ym`（年・月）を `{% if search_mode %}` で囲み、
    週間表示では出さないようにした
- `src/ytsched/webroot/static/css/my.css`
  `.my-month-header` を追加（`#CCC` 地・太字・右側だけ角丸で、日付
  ブロックの `border-radius` と揃えた）
- `tests/test_web.py`
  `TestMonthHeader` を追加（4 件）。既存の `week_panel()` で、いま見て
  いる週のパネルだけを取り出して見ている

`my-date-ym` / `my-date-year` / `my-date-month` の CSS は、検索モードで
使い続けるので残した（「使われなくなる CSS を整理する」は、結果として
消すものが無かった）。

## テスト

verifier（`archives/agents/TODO-147/verifier-report.md`）で確認した。

- `uv run pytest` … 589 件通過。テスト追加後の `tests/test_web.py` は
  149 件通過
- `mise run lint` / `mise run typecheck` … 通過
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、playwright で
  実際の画面を確認。月をまたぐ週（`?date=2026-03-30`）で見出し行が 2 行、
  またがない週（`?date=2026-04-06`）で 1 行。日付欄から年月が消えている
- 検索モードで `my-month-header` が出ず、日付欄に年月が残ること
- 月間表示・ゴミ箱に影響が無いこと
- 画面外の前後の週でも、週ごとに先頭から見出し行が出ること
  （`cur_ym` が週をまたいで持ち越されない）
