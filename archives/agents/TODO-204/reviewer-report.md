# TODO-204 reviewer 報告

対象: 未コミットの `git diff`（`sched_update.py` / `main_handler.py` /
`handler.py` / `tests/test_web.py` / `src/README.md`）と
`webroot/templates/error.html`。

## 確信度の高い指摘

### 1. 編集画面からの新規作成が 409 になる（`sched_update.py` `is_conflict()`）

`is_conflict()` は「`sde_id` が空なら新規作成」として判定を外しているが、
**ブラウザからの新規作成では `sde_id` は空で届かない。**

- 一覧の「新規」は `main-page.js:217` で `sde_id=""` を付けて `/edit/` を開く
- `EditHandler.get()`（`edit_handler.py:126`）は `SchedDataEnt("", date)` を
  作る。コンストラクタ（`ytsched.py:105`）が空の `sde_id` に
  `new_id()`（`…-1`）を振る
- `edit.html:160-161` はその ID を `name="sde_id"` の hidden 相当の入力に
  そのまま出し、`orig_date` にも表示中の日付を出す
- 新規の編集画面のボタンは `update` と `fix`（`edit_menu.html`。`add` は
  `new_flag` のときは出ない）

したがって、新規の編集画面で保存（`fix`/`update`）すると、
`cmd=fix, sde_id=<新しい UUID>-1, orig_date=<その日>` が届き、
`get_sde(orig_date, sde_id)` は必ず `None` → 409 になる。
**画面から予定を新しく作れなくなる。**

in-process で確かめた（scratchpad の一時 datadir。実データは触っていない）:

```
rendered sde_id: fc480c01-3818-4583-9d5b-f79a3746560b-1
is_conflict: True
```

テストが捕まえていない理由: `TestConflict.test_fix_without_sde_id_still_adds`
も既存のテストも、新規は `sde_id=""` で直接 POST しており、編集画面を
経由した値（`…-1`）を送るものが無い。`test_browser.py` の更新ボタンの
テストは既存の予定（`id-{date}`）だけ。

新規を見分ける方法（例えば hidden の `new_flag` を送る、新規では
`sde_id` を出さない、など）は main の判断に任せる。

## 問題の無かった観点

- `cmd` の絞り込み（`fix`/`update` だけ）: 正しい。`del` の空振りは書き込みが
  起きないので対象外、は TODO の決定どおり
- 判定に使う日付: `is_conflict()` と `cmd_del()` はどちらも `form.orig_date`
  をそのまま使うので、見に行くファイルが一致している。ToDo（`orig_date`
  が hidden に出ない → `None` → `ToDo.jsonl`）も、ファイルの無い日
  （空の `SchedDataFile` → `None` → 409）も意図どおり
- 409 の前の副作用: `SchedData.get_sde()` → `get_sdf()` はキャッシュへ
  積む（無い日は空の `SchedDataFile`。ファイルは作らない）だけで、
  ゴミ箱への追記も `_dirty_sdf` への登録も無い。`is_stale()` の読み直しは
  別プロセスの書き換えを拾う方向で害は無い。tornado の同期ハンドラなので
  判定と書き込みの間に他のリクエストは挟まらない
- `write_error()` で `render()`: tornado の文書どおりの使い方
  （`send_error()` が `clear()`・`set_status()` のあとに呼ぶ）。`_app_info` は
  `initialize()` で入るので、XSRF の 403（`prepare()` より前、
  `initialize()` より後）でも使える。TODO-206 は `ERROR_MESSAGES` に
  403 を足すだけで済む形
- `HTTPError` の `log_message` が残るので、409 は tornado のアクセスログ
  / warning に理由付きで出る（黙って失敗していない）
- `test_update_sde_not_found`: 差し替え先が `get_modified_sde` になっても、
  `exec_cmd()` の `sde is None` → 404 の分岐を通る。書き込みまで済んだ
  あとの読み直しで外す、という元のテストの意図も保っている
- `test_404_keeps_default_page`: `/edit` は `EditHandler`（`HandlerBase`
  の子）へ回るので、`write_error()` の `super()` への分岐を実際に通っている
- `src/README.md`: 記述は実装と合っている（ただし指摘 1 が直れば
  「新規は除く」旨の書き足しが要るかもしれない）
- CLAUDE.md の決まり（ログは `mylog`、データ形式の変更なし）からの逸脱なし

## 確信度の低いもの（実害は未確認）

- `error.html` の描画そのものが失敗したとき、`send_error()` は例外を
  `app_log.error` に出して空の本文で 409 を返す。利用者には白い画面に
  なる。テンプレートは定数しか使わないので起きにくい
- `error.html` は `base.html` を継ぐので、一覧用の JS（`week.js`・
  `keyboard.js`・`swipe.js` など）も読み込まれる。一覧の要素が無い画面で
  エラーを出したりキー操作で移動したりしないかは見ていない

## 再レビュー（新規では ID 欄を空にする直し）

対象: `edit.html` の `sde_id` 欄、`test_new_from_edit_page_is_not_409`、
`src/README.md` の 2 行。

### 指摘

無し。

### 見た経路（どれも食い違いなし）

- `fix`/`update`（新規）: `sde_id=""` → `is_conflict()` は外す →
  `exec_update()` は `add_sde_id=""` → `cmd_del(orig_date, "")` は空振り
  （空の `sde_id` の行はコンストラクタが作らないので当たらない）→
  `cmd_add("")` で `new_id()`。ゴミ箱への追記なし
- `update` のあとの編集画面へのリダイレクト: `modified_sde_id` は保存
  された実際の ID で、既存の予定として開く（`new_flag` は偽）ので ID は
  出る
- `edit-page.js` ほか JS: `#sde_id` を読む箇所は無い（新規の画面を開く
  `main-page.js:217` は元から `sde_id: ""`）
- ToDo の新規: 専用の入口は無く、同じ新規の画面で種別を ToDo にする形。
  `orig_date` は表示中の日付で、`cmd_del` は空振り、`cmd_add` が種別で
  `ToDo.jsonl` へ入れる。ID の扱いは通常の予定と同じ
- `add` ボタン: `edit_menu.html` で `new_flag` のときは出ないまま
- `del`（新規の画面）: 前は仮の ID、今は空で、どちらも空振り。挙動は
  変わらない
- テストの強さ: 画面から `sde_id`・`orig_date` を読み取って送るので、
  `edit.html` を戻すと仮の ID が送られて 409 になり、`res.code == 200`
  で落ちる。正規表現の `[^>]*` は改行をまたぐので、属性が 2 行に
  分かれていても拾える
- `src/README.md` の 2 行: 実装と合っている

### 気づき（問題ではない）

- 編集画面から新規作成した予定の最初の版は、前は `…-2`（仮の `-1` の
  `next_id()`）だったが、`add` と同じ `…-1` になる。`add` との食い違いが
  無くなる方向の変化
