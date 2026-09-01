# TODO-139 implementer 報告

## 変更したファイル

- `src/ytsched/trash.py`
  - `TrashFile.delete(sde_id, trashed_at) -> bool` を追加。一致する行
    （複数あれば全て）を取り除いて書き直す。壊れて JSON として読めない
    行は書き直しでも残す。見つからなければ `False`
  - `TrashFile.clear() -> None` を追加。ファイルが無ければ何もしない
  - 書き直しの共通処理として `_write_lines()` を追加。同じディレクトリの
    一時ファイル（`tempfile.mkstemp`）へ書いてから `Path.replace()` で
    差し替える
  - クラス docstring を「全件書き直しもしない」から、追記は書き直さない・
    `delete`/`clear` は書き直す、という説明に直した
- `src/ytsched/trash_handler.py`
  - `post()` の `cmd` を `restore` / `delete` / `clear` に分岐。既存の
    復活処理は `_restore()` へ切り出し、`_delete()`（404 あり）・
    `_clear()` を追加。どちらもゴミ箱画面へ redirect
  - `get()` で `sde_id` をテンプレートへ渡すようにした（絞り込み中かの
    判定に使う）
- `src/ytsched/webroot/templates/trash.html`
  - 各行に削除ボタンを追加（列幅を col-3/3/5/1 → col-2/2/6/2 に振り直し）
  - ヘッダに「空にする」ボタンを追加。`sde_id` 絞り込み中、または
    0 件のときは出さない（0 件のときに空にしても意味が無いため、
    件数 0 も条件に足した。依頼書に無い判断）
  - ゴミ箱が空のとき「ゴミ箱は空です」の 1 行を出す
  - 削除アイコンは `icons.svg` の `#trash`
- `src/ytsched/webroot/static/css/my.css`
  - `.my-trash-restore` に `.my-trash-delete` を相乗り。`.my-trash-clear`
    を新設（`.my-bar` の `color: white` を継承するだけで、新しい色は
    持ち込んでいない）
- `src/ytsched/webroot/static/js/trash-page.js`（新規）
  - `data-confirm` 属性を持つ `<form>` の送信をフックし、`confirm()` が
    キャンセルされたら送信しない
- `tests/test_trash.py`
  - `TrashFile.delete()`/`clear()` の単体テストを追加（1 行だけ消える・
    壊れた行が残る・見つからない場合に `False`・ファイル無しでも
    落ちない、など）
- `tests/test_web.py`
  - `TestTrashHandler` に `cmd=delete`（成功・404）と `cmd=clear` の
    HTTP テストを追加

## 依頼の範囲を超えた判断

依頼書は `onsubmit="return confirm(...)"`（inline event handler）を
指示していたが、`tests/test_web.py::test_templates_have_no_inline_event_handlers`
（TODO-108）に引っかかって落ちた。そのままでは完了条件（`uv run
pytest` が通る）を満たせないため、`data-confirm` 属性 + 新規
`trash-page.js`（`edit-page.js` の `data-action` と同じ IIFE 方式）に
変えた。対象範囲の 5 ファイルに `static/js/` は入っていなかったが、
既存のテスト・慣習と依頼の完了条件の両方を満たすために必要と判断し、
そのまま進めた。

もう 1 点、「空にする」を出す条件に `entry_count > 0` を自分で足した
（依頼書は `sde_id` 絞り込み無しのときだけとしか書いていない）。空の
ゴミ箱を空にする操作は意味が無いための判断。

## 確認したこと

- `uv run pytest`（578 件）が通った
- `uv run ruff format` / `ruff check` / `basedpyright` が通った
  （`ruff format` で `tests/test_web.py` の折り返しが直った以外は
  変更無し。`archives/` 配下の無関係な .md の未フォーマットは既存で、
  今回の変更範囲外）
- 一時データディレクトリでサーバを起動し、`/ytsched/trash` の HTML に
  削除ボタン・空にするボタンが出ること、`cmd=delete`（成功・404）・
  `cmd=clear` を curl で叩いて `trash.jsonl` が期待どおり変わること、
  `sde_id` 絞り込み中と 0 件のときに「空にする」が出ないこと、0 件の
  ときに「ゴミ箱は空です」が出ることを確認した

## 残る懸念

- `src/README.md` は writer が別に直す前提のため触っていない
  （`TrashFile`/`TrashHandler` の説明が古いままの可能性がある）

## 追記: パーミッションの指摘への対応

verifier / reviewer から「`_write_lines()` の書き直しで `trash.jsonl` の
パーミッションが 0644 → 0600 に落ちる（`tempfile.mkstemp()` が 0600 で
作るため）」との指摘。`SchedDataFile.save()` の慣習に合わせ、元ファイルが
あれば `os.fchmod()` で一時ファイルへパーミッションを引き継ぐよう
`_write_lines()` を直した。元ファイルが無いとき（`delete()` は必ず既存
ファイルを前提にしているので実際には起きないが、念のため）は一時ファイル
既定のパーミッションのまま書く、と docstring に明記した。

- `tests/test_trash.py` に `test_delete_keeps_original_permissions` を
  追加（0644 に chmod してから `delete()` し、0644 のままであることを
  確認）
- `uv run pytest tests/test_trash.py`（15 件）、`uv run ruff format
  --check` / `ruff check` / `basedpyright` を確認。全テストの再実行は
  行っていない

## 追記: スマホ幅（390px）の崩れの修正

`~/tmp/playwright-mcp/ytsched-trash-list.png` で見つかった 5 点を直した。

1. **ヘッダを 1 行に戻し、「空にする」を `<main>` の末尾（リストの
   一番下）へ移した。** ヘッダ 2 行化で 1 件目がヘッダの下に隠れていた
   原因を直接絶った。`trash_handler.py` は変更していない
   （`sde_id`/`entry_count` は元から渡している）
2. 列幅を `col-2/2/6/2` から **`col-3/2/4/3`**（日付/時刻/種別・タイトル/
   ボタン）に振り直した。日付 `2026/09/06 (Sun)` が 1 行に収まるように
3. **`d-inline` は、このプロジェクトに存在しないクラスだった
   （TODO-047 で Bootstrap をやめ、独自の `.row`/`.col-N` に置き換えて
   あり、`d-inline` は無い）。** そのままではボタンが縦に並んだままに
   なる。ボタンを包む `div` に `.my-trash-actions`（`display: flex;
   justify-content: flex-end; gap: 0.5rem`）を新設して直した
4. `entry.trashed_at` の表示を `.split('.')[0].replace('T', ' ')` にし、
   マイクロ秒を削って秒までにした。保存している値自体は変えていない
5. `.my-trash-delete` と `.my-trash-clear` に `color: #C33`（控えめな赤）
   を追加。アイコンは `stroke: currentColor` なので、色を継承してアイコン
   ごと赤くなる

### 確認したこと

- `tools/screenshot.py` で幅 390px のスクリーンショットを撮り直し、
  10 件・1 件・0 件の 3 パターンを目で確認した
  - 10 件: `~/tmp/playwright-mcp/ytsched-trash-list2.png`
    （`ytsched-trash-list2_closed_390.png` と同じ内容）。ヘッダ 1 行、
    1 件目が隠れない、日付が 1 行に収まる、復活・削除ボタンが横に並ぶ、
    削除日時が秒まで、削除系ボタンが赤いことを確認
  - 1 件: `ytsched-trash-one_closed_390.png`。「空にする」がリストの
    直後（一番下）に出る
  - 0 件: `ytsched-trash-empty2_closed_390.png`。「ゴミ箱は空です」が
    出て、「空にする」は出ない
  - **テンプレートを直したあと、動かしっぱなしの `uv run ytsched
    webapp` を再起動しないと変更が反映されないことに気付いた**
    （tornado がコンパイル済みテンプレートをキャッシュするため）。
    1 回目のスクリーンショットで直っていないように見えたのはこれが原因
    で、再起動後に撮り直して直っていることを確認した
- `uv run pytest tests/test_web.py tests/test_trash.py`（155 件）、
  `uv run ruff check src/ tests/` / `ruff format --check src/ tests/` /
  `basedpyright` を確認。全テストの再実行は行っていない
