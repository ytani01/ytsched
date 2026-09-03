# TODO-166. 月間表示の先読み画面数を `LoadMonthPages` で変えられるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | implementer + verifier |
| 消費 | output 17,370 / cache_creation 144,403 / 概算 $2.4 |
|      | main 66% + implementer 22% + verifier 12%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-166/](../agents/TODO-166/README.md) にある。

## きっかけ

月間表示（TODO-137）は 6 ヶ月ぶんの画面を 1 ブロックとして、前後 1 つずつ
＝ 3 画面（18 ヶ月）を HTML に入れていた。この数が `_mk_month_blocks()` に
`(-1, 0, 1)` とハードコードされていて、利用者が変えられなかった。週間表示には
`LoadMonths` があるので、月間表示にも同じ形の設定を置いた。

## やったこと

- **`conf.json` に `LoadMonthPages` を足した**（既定 2、範囲 0〜10）。
  値は「前後に持つ 6 ヶ月画面の数」で、`n` なら `2n + 1` 画面ぶんを HTML に
  含める。`MainBinder` の `_get_conf_int()` で読むところまで、`LoadMonths` と
  同じ形にした（`DisplayArgs.load_month_pages`）
- **`_mk_month_blocks()` の `for offset in (-1, 0, 1)` を
  `range(-n, n + 1)` にした。** 既定が 2 なので、月間表示は
  **3 画面（18 ヶ月）から 5 画面（30 ヶ月）になった**
- 文書（`src/README.md`・`docs/User.md`・`tests/README.md`）とテストの
  「3 ブロック＝18 ヶ月」を書き直した

範囲を `LoadMonths` の 0〜24 に揃えず 10 で止めたのは、月間表示は 1 画面が
6 ヶ月ぶんあり、同じ数値でも読み込む量がまるで違うため。上限の 10 でも
21 画面（126 ヶ月）になる。画面数が増えるぶん `load_month_cal()` の
`os.stat()` も増えて遅くなるが、設定で戻せるので既定を 2 にした。

JS・CSS は触っていない。`week.js` の `layoutWeeks()` が `activeWeekOffset`
からの相対位置で `my-week-cur` / `my-week-near` を付け替えるので、画面が
増えても端は `display: none` のまま。

## テスト

- `_mk_month_blocks()` の単体テストを、既定で `[-2, -1, 0, 1, 2]` の
  5 ブロックになる形に書き直した（`tests/test_main_handler.py`）
- `LoadMonthPages` の値ごとの動きを見るテストを足した
  （`tests/test_web.py`。`LoadMonths` のテスト群が手本）。
  `0` で 1 ブロック、`3` で 7 ブロック、範囲外・数字でない値は既定の
  5 ブロックへ落ちる
- verifier が実際に起動して、`?view=month` の `data-block=` の数を数えた。
  未設定 5 / `"0"` 1 / `"10"` 21 / `"11"`・`"-1"`・`"abc"` は 5 と警告ログ。
  週間表示（`LoadMonths`）への影響も無し
- `ruff format` / `ruff check` / `basedpyright` / `pytest`（619 件）が通る
