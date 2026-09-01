# TODO-139 implementer への依頼

## 目的

ゴミ箱画面（`/ytsched/trash`）に、消えた予定を **1 件ずつ完全に消す** UI と、
**全部まとめて消す**（ゴミ箱を空にする）UI を足す。いまは「復活」しか無い。

## 対象範囲

触るのは次の 5 つだけ。他のファイルは変えない。

1. `src/ytsched/trash.py` — `TrashFile` に 1 行削除と全消去を足す
2. `src/ytsched/trash_handler.py` — `post()` に `cmd=delete` / `cmd=clear`
3. `src/ytsched/webroot/templates/trash.html` — ボタン
4. `src/ytsched/webroot/static/css/` のゴミ箱用 CSS — 必要なら
5. `tests/test_trash.py` — テスト

`src/README.md` は writer が別に直すので触らない。

## 決めてあること（変えない）

- **消したら戻せないので、どちらも確認をはさむ。** ブラウザ側の
  `confirm()` で足りる（単一ユーザ用のアプリ）
- **`.bak` は作らない。** ゴミ箱のゴミ箱になって意味が無い
- **1 行削除では `trash.jsonl` を全件書き直す。** `TrashFile` の
  「全件書き直しもしない」と書いてある docstring も合わせて直す
- **`?sde_id=` で絞り込んで開いているときは「空にする」を出さない。**
  出ているものだけが消えるのか全部消えるのかが紛らわしいため。絞り込み
  無しのときだけ出し、消すのは `trash.jsonl` 全体
- 復活と同じく **POST → redirect**（`TrashHandler.post()` は描かずに
  ゴミ箱画面へ戻す）。復活だけが一覧へ飛ぶ現状の動きは変えない

## 実装の指針

### `TrashFile`（`trash.py`）

- `delete(sde_id, trashed_at) -> bool` — 一致する 1 行だけを取り除いて
  書き直す。消せたら `True`、見つからなければ `False`
  - 同じ `sde_id` と `trashed_at` の行が複数あることは無い想定だが、
    あったときにどうするかは docstring に書くこと
  - **壊れた行を巻き添えにしない。** `entries()` は壊れた行を警告して
    飛ばすが、書き直しでそれを消してしまうと復旧の手がかりが失われる。
    読めない行はそのまま残す
  - 書き直しは、同じディレクトリの一時ファイルへ書いてから
    `os.replace()` で差し替える（途中で落ちたときに全部失わないため）
- `clear() -> None` — `trash.jsonl` 全体を空にする。ファイルが無いときは
  何もしない（例外にしない）

### `TrashHandler`（`trash_handler.py`）

- `post()` の `cmd` を `restore` / `delete` / `clear` の 3 つに分ける。
  知らない `cmd` は今までどおり 400
- `delete` は `sde_id` と `trashed_at` を受け取る。見つからなければ 404
- `clear` は引数を取らない
- `delete` / `clear` のあとは、ゴミ箱画面へ redirect する

### `trash.html`

- 各行に削除ボタンを足す。いまの復活ボタンの隣に置く。列幅
  （`col-1` など）は崩れないように振り直すこと
  - アイコンは `icons.svg` の `#trash` を使う
  - `onsubmit="return confirm(...)"` で確認する。文面は
    「この 1 件を完全に消します。よろしいですか?」のような、消えるものが
    分かる短い日本語にする
- ヘッダに「空にする」ボタンを足す（`sde_id` で絞り込んでいないときだけ）。
  こちらも `confirm()` で確認し、文面に件数を入れる
- ゴミ箱が空のときは、いまは何も出ない。「ゴミ箱は空です」のような
  1 行を出す

CSS は既存の `.my-trash-*` に合わせる（`.my-trash-restore` が下敷きに
なる）。新しい色や大きさを持ち込まないこと。

## 完了条件

- `uv run pytest` が通る
- `uv run ruff format` / `uv run ruff check` / `uv run basedpyright` が
  通る（`mise run upgradeproject` は**走らせない**）
- `tests/test_trash.py` に、少なくとも次を足す
  - `delete()` で 1 行だけ消えること、他の行と壊れた行が残ること
  - 見つからない `trashed_at` で `False` が返ること
  - `clear()` でファイルが空になること、ファイルが無くても落ちないこと
  - `TrashHandler` の `cmd=delete` / `cmd=clear`（`tests/test_web.py` の
    やり方に合わせてよい。既存のゴミ箱の HTTP テストがどこにあるかは
    `tests/README.md` と `tests/test_web.py` を見て決めること）

## 報告

`archives/agents/TODO-139/implementer-report.md` に、変更点・検証結果・
残る懸念を書く。返事は「終わったか・報告ファイルのパス・判断が要る点」の
5 行以内にすること。
