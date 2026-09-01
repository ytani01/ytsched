# TODO-148. ゴミ箱の予定を、検索結果と同じ見た目にする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 34,540 / cache_creation 412,524 / 概算 $5.8 |
|      | main 45% + implementer 31% + verifier 13% + reviewer 11%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-148/](../agents/TODO-148/README.md) にある。

## きっかけ

ゴミ箱画面だけが独自の 1 行レイアウト（`.my-trash-entry-row` に日付・
時刻・種別 + タイトルを横に並べる）で、週間表示・検索表示と見た目が
揃っていなかった。

着手前に確かめたこと:

- まとめ方は、重複グループの「同じ予定の内容が N 件」を残す
  （日付ごとにまとめ直さない）
- 予定の本体は `sde.html` を共有する（似せて書き直さない）
- 削除日時は、予定の下に今までどおり出す
- 復活ボタンとチェックボックスは、見た目も動きも今のまま

## やったこと

- `sde.html` が受け取る変数を 2 つ増やした
  - `sde_editable`（bool）… False のときは `my-btn` も
    `data-action="edit-sde"` も付けない。ゴミ箱の予定は編集できない
  - `sde_uniq`（str）… 詳細の折りたたみの `sw_id` を一意にする接尾辞。
    ゴミ箱では同じ `sde_id` の予定が複数並ぶので、
    `'sw%s-%s' % (sde_id, today_flag)` だけでは DOM の id が衝突する
- `main.html` 側で `sde_editable = True` / `sde_uniq = ''` を設定した。
  `sde_uniq` が空文字なので、`sw_id` の値は今までと同じまま
- `trash.html` の 1 件ぶんを、検索結果と同じ `.my-date-block`
  （`.my-date-col` + `.my-day-entries` + `.my-trash-actions`）へ
  書き直した。日付欄の中身は検索結果と同じで、今日の予定には
  `.my-date-block-today` が付く
- `trash_handler.py` の `render()` に `today` を渡した
  （今日からの差と、今日かどうかの判定に要る）
- CSS は `.my-trash-entry .my-day-entries { grid-column: span 9; }` を
  足し、`.my-trash-actions` を span 3 から span 2 にした
  （12 列の内訳が 1 + 9 + 2）。共通の `.my-day-entries`（span 11）は
  そのまま。使われなくなった `.my-trash-entry-row`
  `.my-trash-date-col` `.my-trash-time-col` `.my-trash-entry-summary`
  `.my-trash-detail` を消した

`<article>` に付いていた `my-sde my-sde-normal` は外した。`sde.html` を
include すると内側にも `.my-sde` が出て、枠と背景が二重になるため。
外の枠は `.my-date-block`、内の色分けは `sde.html` の `.my-sde` が
持つ形になり、検索結果と同じ構造になった。

Tornado のテンプレートには Jinja の `loop.index` に相当するものが
無いので、`sde_uniq` は `{% for i, x in enumerate(...) %}` の
`group_index` と `entry_index` の組で作っている。

## テスト

- `uv run pytest` … 595 件全通過
- `ruff format --check` / `ruff check` / `basedpyright` / `mypy` … 通過
- 足したテスト
  - `tests/test_web.py::test_entry_has_date_column_like_search_result`
    … 日付欄・`sde.html` の描画が出ていること、`<main>` 内に
    `data-action="edit-sde"` が出ていないこと
  - `tests/test_browser.py::test_trash_entry_shows_date_column_like_search_result`
    … 予定の本文をクリックしても編集画面へ遷移しないこと
- verifier が一時ディレクトリでアプリを起動し、週間・月間・検索・
  ゴミ箱の 4 画面が 200 で出ること、折りたたみの id が重複しないこと、
  復活と一括削除が動くことを確かめた
- reviewer の指摘は「`.my-trash-actions` を span 2 に狭めた見た目を
  確認していない」の 1 件のみ。実際にスクリーンショットを撮って、
  復活ボタンとチェックボックスが崩れずに収まっていることを確かめた
