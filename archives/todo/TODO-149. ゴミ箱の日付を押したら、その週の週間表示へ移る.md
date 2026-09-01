# TODO-149. ゴミ箱の日付を押したら、その週の週間表示へ移る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Sonnet 5 / effort medium | main のみ + verifier |

## きっかけ

TODO-148 でゴミ箱の予定を検索結果と同じ見た目にしたが、日付欄は押しても
何も起きないままになっていた。検索結果では日付欄を押すとその日の週へ移る
ので、ゴミ箱でも同じように移れるようにする。

遷移は月間表示の日付セル（`data-action="week-date"`）と同じ形にする。
`date` とその日を上端に寄せる `sde_align=top` を付けた GET で、`view` は
付けない（週間表示で開く）。検索結果の `date-post` は検索の解除を伴う
POST なので、ゴミ箱では使わない。

## やったこと

- `trash.html` の日付欄（`.my-date-col`）に `my-btn` クラスと
  `data-action="week-date"`・`data-date="{{ sched_date }}"` を追加した
- `trash-page.js` に `[data-action="week-date"]` へのクリック委譲を足し、
  `window.ytsched.doGet(window.ytsched.url_prefix, { date, sde_align: "top" })`
  を呼ぶようにした
- `ytsched.doGet()` は `loadingSpinner()` を呼ぶが、`trash.html` には
  `#loadingSpinner` 要素も、`ytState.elLoadingSpinner` を設定する処理も
  無かった。呼ぶと `null.style` の参照で例外になり、`location.href` へ
  進む前に処理が止まってナビゲーションが起きない不具合になっていた
  （ブラウザテストで実際に踏んだ）。`trash.html` に `#loadingSpinner`
  要素を足し、`trash-page.js` の `load` ハンドラで
  `ytState.elLoadingSpinner` を設定するようにして直した（main.html・
  edit.html と同じ形）
- `tests/test_web.py` にテストを足した
  - `test_entry_date_column_has_week_date_action` … 日付欄に
    `data-action="week-date" data-date="2021-03-01"` が出ること
- `tests/test_browser.py` にテストを足した
  - `test_trash_date_column_click_moves_to_that_week` … 日付欄を押すと
    `?date=2026-08-20&sde_align=top` へ遷移し、その週（月曜
    2026-08-17・木曜 2026-08-20 の両方）が画面に出ること

## テスト

- `uv run pytest` … 597 件全通過
- `ruff format --check` / `ruff check` / `basedpyright` / `mypy` … 通過
  （`ruff format --check` の未整形指摘は `archives/` 内の既存 `.md` ・
  `.py` ファイルで、今回の変更とは無関係）
- verifier が `tests/test_web.py -k trash`・`tests/test_browser.py -k
  trash` を実行し全通過を確認、一時ディレクトリでアプリを起動して
  ゴミ箱の日付欄をクリックし、実際にその週の週間表示（月曜・木曜が
  両方表示される）へ移ることを確認した。ゴミ箱の予定本体をクリックしても
  編集画面へ遷移しない（TODO-148 の挙動）ことも合わせて確認した
