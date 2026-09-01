# TODO-148 implementer 報告

## 変更したファイル

- `src/ytsched/webroot/templates/sde.html`
  - `sde_editable`（bool）・`sde_uniq`（str）を受け取る変数に追加。
    冒頭コメントの一覧も書き足した。
  - `sde_editable` が False のときは `.my-sde-content-col` に
    `my-btn` を付けず、`data-action="edit-sde"` /
    `data-date` / `data-sde-id` / `data-todo-flag` も出さない。
  - 詳細の折りたたみの `sw_id` に `sde_uniq` を混ぜて、同じ
    `sde_id` の予定が複数並んでも DOM の id が衝突しないようにした。
- `src/ytsched/webroot/templates/main.html`
  - `{% include sde.html %}` の直前で `sde_editable = True` /
    `sde_uniq = ''` を設定（`main.html` からの利用は今までどおり
    編集可能）。
- `src/ytsched/webroot/templates/trash.html`
  - 1 件ぶんを `.my-date-block`（`.my-date-col` + `.my-day-entries`
    + `.my-trash-actions`）の形に書き直した。日付欄は検索結果と同じ
    中身（年・月・日・曜日・今日からの差）で、今日の予定には
    `my-fw-bold` と `.my-date-block-today` を付ける。
  - `.my-day-entries` の中で `{% include sde.html %}` を呼び、
    `sde_editable = False` を渡す。
  - 復活ボタン・チェックボックスは `.my-trash-actions` にそのまま
    残し、属性（`data-sde-id` / `data-trashed-at` / `aria-label`）は
    変えていない。削除日時の行・重複グループの見出しもそのまま残した。
  - `sde_uniq` は `group_index` と `entry_index`（どちらも
    `enumerate()`）を組み合わせて、ページ全体で一意にした。
- `src/ytsched/trash_handler.py`
  - `render()` に `today=datetime.date.today()` を追加。
- `src/ytsched/webroot/static/css/my.css`
  - 使われなくなった `.my-trash-entry-row` `.my-trash-date-col`
    `.my-trash-time-col` `.my-trash-entry-summary` `.my-trash-detail`
    を削除（削除前に grep でどこからも参照されていないことを確認済み。
    テンプレート・Python・テストのどこにも残っていない）。
  - `.my-trash-actions` の `grid-column` を `span 3` から `span 2` に
    変更（12 列グリッドの内訳を `.my-date-col`(1) +
    `.my-day-entries`(9) + `.my-trash-actions`(2) に合わせた）。
  - `.my-trash-entry .my-day-entries { grid-column: span 9; }` を
    足し、共通の `.my-day-entries`（span 11）はそのまま。
- `tests/test_web.py`
  - `TestTrashHandler` に
    `test_entry_has_date_column_like_search_result` を追加。
    `.my-date-block` / `.my-date-col` / `.my-wday-0` / 年月日・曜日の
    表示、`.my-sde-type` / `.my-sde-title`（= `sde.html` の描画）が
    出ていること、`<main>` 内に `data-action="edit-sde" data-date=`
    が出ていないことを確認する。
- `tests/test_browser.py`
  - `test_trash_entry_shows_date_column_like_search_result` を追加。
    `.my-trash-entry .my-date-col` が件数ぶん出ること、日付・曜日の
    表示、`.my-sde-content-col` をクリックしても編集画面へ遷移しない
    ことを確認する。

## 判断が要った点

1. **`sde.html` の入れ子で `.my-sde` が二重になる問題**
   もとの `trash.html` の `<article>` に `my-sde my-sde-normal` が
   付いていたが、`sde.html` を include すると内側にも `.my-sde` が
   出て二重になる（外側の枠・背景が予定の色分けと衝突する）。
   `<article>` からは `my-sde my-sde-normal` を外し、`my-trash-entry`
   だけにした。見た目の枠・背景は `.my-date-block`（外）と
   `sde.html` が出す `.my-sde`（内、`.my-day-entries` の中）が
   それぞれ担う、検索結果と同じ構造にした。

2. **今日の予定に `.my-date-block-today` を付けるかどうか（今回の
   指示で判断を求められた点）**
   ゴミ箱の各エントリは `today_flag`（`sched_date == today`）を
   すでに持っていたので、検索結果・週間表示と揃えて
   `.my-date-block-today`（太い青枠）を付けることにした。ゴミ箱に
   並ぶ予定はすでに削除済みで、日付が「今日」かどうかに強い意味は
   薄いが、見た目を検索結果に揃えるという TODO-148 の趣旨に沿う
   ほうを選んだ。

3. **`sde_uniq` の組み立て方**
   Tornado テンプレートには Jinja の `loop.index` に相当するものが
   無いため、`{% for i, x in enumerate(...) %}` の形にした
   （`enumerate` は既存コードの `len()` / `str()` / `int()` と同じ
   ビルトイン経由で使える）。`group_index` と `entry_index` の組で
   ページ内一意性を確保した。

## 確認したこと

- `uv run pytest tests/test_web.py -k Trash` … 19 件通過
- `uv run pytest tests/test_browser.py -k trash` … 3 件通過
- `uv run pytest -q`（フォアグラウンド、単独実行） … **595 件全通過**
  （途中でバックグラウンドでも同時に走らせたところ、フッターの
  自動ページ送り系のテストが 2 件、タイミングで失敗した。同じ
  サーバ・ポートを使う `pytest` を並行して 2 つ走らせたことが原因で、
  今回の変更とは無関係。単独のフォアグラウンド実行では全通過して
  いるので問題ない）
- `uv run ruff format --check src tests` … 35 files already formatted
- `uv run ruff check src tests` … All checks passed
- `uv run basedpyright` … 0 errors
- `uv run mypy src` … Success
- `grep` で `.my-trash-entry-row` `.my-trash-date-col`
  `.my-trash-time-col` `.my-trash-entry-summary` `.my-trash-detail` が
  テンプレート・CSS・Python・テストのどこからも参照されていないこと
  を確認してから削除した

## 残る懸念

- 特になし。完了条件（テスト・lint・見た目・復活/選択/一括削除の
  動作）はすべて確認済み。
