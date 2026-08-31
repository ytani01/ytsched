# TODO-132. ミニカレンダーの ToDo の枠を太くし、重要な ToDo を赤にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 18,195 / cache_creation 193,878 / 概算 $2.4 |
|      | main 48% + implementer 33% + verifier 19%（料金の割合） |

分担と担当の報告は
[archives/agents/TODO-132](../agents/TODO-132/README.md) にある。

## きっかけ

TODO-131 で ToDo の四角を枠のみにしたが、枠が 1px で見えにくかった。
また、重要（タイトルが `!` 始まり）を赤にする扱いは予定のドット
（`has_important`）にしかなく、ToDo には効いていなかった。
`load_month_cal()` が ToDo を除いた `sde_list` だけを見ていたため。

## やったこと

### 四角の枠を太くする

`src/ytsched/webroot/static/css/my.css` の `.my-mini-cal-sq` を
`border: 1px solid #28F` から `2px solid #28F` にした。`*` に
`box-sizing: border-box` が効いているので、外寸は 6px のままで、
ドットと大きさが揃う。内側の空きは 2px になる。

外寸を 8px にして枠の内側を広く残す案もあったが、ドットより大きく
なるので採らなかった。

### 重要な ToDo を赤にする

`MonthCalDay` に `has_todo_important` を足し、`load_month_cal()` で
埋めるようにした。判定は `has_todo` と同じ 2 経路。

- `ToDo.jsonl`（`get_sdf(None)`）の締切日のうち、`is_important()` が
  真のもの
- 日付ファイルに混ざった ToDo 型の行のうち、`is_important()` が真の
  もの（TODO-129 で `has_todo` に足したのと同じ経路）

`ToDo.jsonl` の走査は `_build_todo_dates()` にまとめ、締切日の集合と
重要な締切日の集合を 1 回の走査で作る。キャッシュして 1 リクエスト内で
1 回だけ集めるのは元のまま。

テンプレート側は `main.html` で、`has_todo_important` のとき四角に
`my-mini-cal-sq-important` を足す。CSS では `border-color: #E33` だけを
変え、塗りつぶしはしない。TODO-131 で決めた「ToDo は枠のみ」を保つため。

取り消し済み（`(欠)` 始まり）を重要としないのは、既存の
`is_important()` の判定にそのまま従う。

## テスト

`tests/test_main_handler.py` に 3 件足した。

- `test_todo_deadline_sets_has_todo_important` — 重要な ToDo の締切日が
  真、ふつうの ToDo の締切日が偽
- `test_canceled_important_todo_is_not_important` — 取り消し済みの重要な
  ToDo は偽
- `test_todo_in_day_file_important_is_shown_as_important` — 日付ファイル
  に混ざった重要な ToDo 型の行でも真になる（verifier の指摘で追加）

`mise run fmt` / `typecheck` / `lint` と `uv run pytest`（556 passed）が
通ることを verifier が確認した。一時ディレクトリにデータを作って
アプリを起動し、HTML の `class` 属性とスクリーンショットの両方で、
青ドット（予定）・青枠の四角（ToDo）・赤枠の四角（重要な ToDo）が
出ることを確かめた。
