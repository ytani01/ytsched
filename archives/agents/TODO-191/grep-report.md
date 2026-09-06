# TODO-191 調査報告（grep 版）

道具の制約: Read / Grep / Glob と Bash の `cat` / `grep` / `sed` / `find` のみ。
CodeGraph（`codegraph` コマンド・MCP ツール・`.codegraph/`）は一切使っていない。

## 1. Web からの復元操作の経路

- `trash.html` の各行の復元フォームは `POST {url_prefix}trash` へ
  `cmd=restore`・`sde_id`・`trashed_at` を送る
  （`src/ytsched/webroot/templates/trash.html:94-99`）。
- ルーティングは `src/ytsched/webapp.py:106-107` で
  `{url_prefix}/trash` → `TrashHandler` に割り当てられている。
- `TrashHandler.post()`（`src/ytsched/trash_handler.py:76-83`）が
  `cmd == "restore"` を見て `self._restore()` を呼ぶ（79 行目）。
- `TrashHandler._restore()`（`trash_handler.py:114-135`）が本体:
  1. `sde_id` / `trashed_at` を引数から取り、
     `TrashFile.get(sde_id, trashed_at)`（`trash.py:170-179`）で
     `trash.jsonl` から該当行（`TrashEntry`）を探す
     （`trash_handler.py:115-119`）。無ければ 404。
  2. `self._restore_id(sde)`（`trash_handler.py:85-112`、後述）で
     復元後の `sde_id` を決める。
  3. `SchedDataEnt` を新しく組み立て、タイトルの先頭に
     `(復活)` を付ける（`trash_handler.py:123-132`）。
  4. `self._sd.add_sde(restored.date, restored)`
     （`trash_handler.py:133`）→
     `SchedData.add_sde()`（`ytsched.py:1051-1071`）が
     `self.get_sdf(date)`（`ytsched.py:967-1019`）でその日付の
     `SchedDataFile` を取得し、`sdf.add_sde(sde)`
     （`SchedDataFile.add_sde()`, `ytsched.py:781-790`）でメモリ上の
     一覧へ追加し、`self._dirty_sdf[date] = sdf` で「変更あり」に
     マークするだけで、この時点ではまだファイルに書かれない
     （`add_sde()` の docstring どおり、保存は `save()` にまとめる
     設計、TODO-077）。
  5. `self._sd.save()`（`trash_handler.py:134`）→
     `SchedData.save()`（`ytsched.py:1107-1121`）が `_dirty_sdf` に
     載っている `SchedDataFile` ごとに `sdf.save()` を呼ぶ。
  6. `SchedDataFile.save()`（`ytsched.py:738-779`）が実際の書き込み。
     既存ファイルが空でなければ `.bak` へ退避してから
     （762-766 行目）、`self.pathname` へ全件を書き直す
     （770-773 行目）。書き込み先のパスは `SchedDataFile.date2path()`
     （`ytsched.py:504-`）が決める `{topdir}/{年}/{月}/{日}.jsonl`
     （`sde.date` が今日以前でも、復元した予定の `date` フィールドの
     年月日で決まる。`date` が `None`＝ToDo なら `ToDo.jsonl`）。
  7. 最後に `self.redirect(...)`（`trash_handler.py:135`）で
     `{url_prefix}?date={restored.date}` へリダイレクトする。

まとめると、経路は
`trash.html`（フォーム）→ `TrashHandler.post`（`trash_handler.py:76`）
→ `TrashHandler._restore`（`trash_handler.py:114`）
→ `SchedData.add_sde`（`ytsched.py:1051`）
→ `SchedData.save`（`ytsched.py:1107`）
→ `SchedDataFile.save`（`ytsched.py:738`）
→ 実データファイル（`{年}/{月}/{日}.jsonl` または `ToDo.jsonl`）
という順。

## 2. 復元された予定の `sde_id` の版番号の扱い

`TrashHandler._restore_id()`（`trash_handler.py:85-112`）が決める。

- `SchedDataEnt.split_id(sde.sde_id)`（`ytsched.py:256-272`）で
  元の ID を UUID 部分と版に分ける。新形式（`{UUID}-{版}`）でなければ
  `None` を返し、呼び出し元（`_restore()`）はその `None` を
  `SchedDataEnt` のコンストラクタへそのまま渡す。コンストラクタ
  （`ytsched.py:87-` 付近、`self.sde_id = sde_id if sde_id else
  SchedDataEnt.new_id()`）が `sde_id` が偽（`None`）なら
  `new_id()`（`ytsched.py:249-253`、`uuid.uuid4()` を新規発行し
  版 1）を割り当てる。つまり**旧形式の ID は、UUID ごと新規に
  発行し直す**。
- 新形式であれば、`trash_handler.py:106-110` で
  - `self._trash().max_version(uuid_part)`
    （`TrashFile.max_version()`, `trash.py:181-195`。ゴミ箱
    `trash.jsonl` 全体を見る）
  - `self._sd.max_version(uuid_part)`
    （`SchedData.max_version()`, `ytsched.py:1123-1165`。ゴミ箱を
    除いたデータディレクトリ全体――日々のファイルと `ToDo.jsonl`
    ――を走査する。`ytsched.py:1129` のコメントどおり
    `trash.jsonl` はここでは見ない）
  - 復元しようとしている当該行自身の `version`
    の 3 つの最大値 (`max()`) を取り、その **+1** を新しい版として
    `SchedDataEnt.format_id(uuid_part, max_version + 1)`
    （`ytsched.py:297-299`）で組み立てる（`trash_handler.py:112`）。
- コメント（`trash_handler.py:90-96`）にあるとおり、復元先の日付の
  ファイルだけでなくデータディレクトリ全体を見るのは、日付を変える
  編集で生きている予定が別の日付のファイルへ移っていても見落とさない
  ため（TODO-171 で reviewer の指摘を受けて全走査にした、との説明）。
- 復元後のタイトルには `(復活)` が先頭に付く
  （`trash_handler.py:129`）。日付・時刻・種別・場所・詳細は
  ゴミ箱の内容をそのまま引き継ぐ（`trash_handler.py:123-132`）。

## 3. 復元後、ゴミ箱側のエントリがどうなるか

**`_restore()` はゴミ箱の行を消していない。**
`TrashHandler._restore()`（`trash_handler.py:114-135`）を読む限り、
`TrashFile.delete()` / `TrashFile.delete_many()`（`trash.py:197-245`。
ゴミ箱を完全に消す唯一の手段）を呼ぶ行は無い。`SchedData.add_sde()`・
`SchedData.save()`・`SchedDataFile.save()`（前述の経路）のどこにも
`trash.jsonl` を書き換える処理は無い（`SchedData.del_sde()`
（`ytsched.py:1073-1105`）が `trash.jsonl` へ**追記**する処理を持つ
のみで、これは削除時の経路であり復元時には呼ばれない）。

したがって、復元してもゴミ箱のその行はそのまま `trash.jsonl` に
残り続ける。ゴミ箱の一覧画面（`GET /trash`、`TrashHandler.get()`,
`trash_handler.py:53-74`）に、復元済みの行も引き続き表示される
（`trash.html:110` の「版 N ・ … に削除」という表示がそのまま出る）。
消すには、ゴミ箱画面から選んで `cmd=delete_many`
（`TrashHandler._delete_many()`, `trash_handler.py:137-162`）を
明示的に叩く必要がある。

## 確信が持てなかった点

- `ytsched.py:1153` の
  `except UnicodeDecodeError, json.JSONDecodeError:` は、一見
  Python 2 風の構文に見えたが、`ast.parse()` で確認したところ
  実際には構文エラーにならず、括弧なしのタプルとして
  `except (UnicodeDecodeError, json.JSONDecodeError):` と同じ意味に
  解釈されるようだった。今回の設問（復元の経路）には直接関係しない
  （`SchedData.max_version()` 内の壊れた行の読み飛ばし処理）ので、
  詳しくは追っていない。
- 「復元してもゴミ箱の行が残る」のが意図した仕様か、見落とし
  （本来は消すべきところを実装し忘れたのか）かは、コードとコメント
  だけからは判断できなかった。`trash_handler.py` や `trash.py` の
  コメントにも、復元後にゴミ箱の行をどう扱うかについての言及は
  見当たらなかった。
