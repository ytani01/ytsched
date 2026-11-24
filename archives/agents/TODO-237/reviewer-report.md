# TODO-237 reviewer 報告

対象: `git status --short` に出る未コミットの変更すべて（`attach.py`・`attach_handler.py`・`test_attach.py` を含む）。
修正はしていない。原因も調べていない。確かめたことは、使ったファイル名や値を書いている。

## 要修正

### 1. 先頭が `.` と空白の名前は、置けるが開けず、外せもしない（`src/ytsched/attach.py` の `safe_name()`、`is_valid_name()`）

`safe_name()` は `strip()` してから `lstrip(".")` するので、`.` を除いたあとに先頭の空白が残る。
そのため `safe_name()` を 2 回通すと結果が変わり、`is_valid_name()`（`safe_name(name) == name`）が、
自分で置いた名前を受け付けない。

実測（スクラッチパッドで `AttachStore` と `make_app()` を使って確認した）:

- `add(sde_id, ". a.png", ...)` は `" a.png"` という名前で置く
- `is_valid_name(" a.png")` は False
- `GET /ytsched/attach/{UUID}/%20a.png` は 404
- `remove(sde_id, " a.png")` は何もせずに戻り、`list_files()` には `" a.png"` が残る

起きる入力は、アップロードするファイル名が `.` の並びと空白で始まるとき（`". a.png"`、`"... メモ.pdf"` など）。
編集画面では「外す」の欄とリンクが出るが、リンクは 404 になり、外しても消えない。
項目の箇条「1 つずつ外せる」「ハンドラ」の両方に反する。ただし、こういう名前のファイルはめったに無い。
`test_safe_name` はこの場合を見ていない。

## 検討

### 2. ファイル名が長すぎると、予定は保存されたまま 500 になる（`attach.py` の `add()`、`sched_update.py` の `exec_update()`）

`add()` の `path.open("xb")` は、名前が FS の上限（ext4 は 255 バイト）を超えると `OSError` を出す。
`update_attachments()` は `self._sd.save()` のあとに呼ばれ、`MainHandler.post()` は例外を受け止めないので、
予定は保存済み、`attach_del` は適用済み、残りのファイルは置かれないまま 500 になる。

実測: `add(sde_id, "あ" * 90 + ".pdf", b"x")` は `OSError [Errno 36] File name too long`。
Web 経由で 500 になることは、コードを読んだだけで、動かしてはいない。
起きる入力は、UTF-8 で 255 バイトを超えるファイル名（日本語ならおよそ 85 文字超）。macOS の APFS は
UTF-16 で 255 文字まで許すので、Mac からなら持ち込める。同名で `-1` を付けたときに上限を超える場合も同じ。
実際に起きそうかは確かめていない。

### 3. 文書のうち、変更に合わせて直っていないもの（`src/README.md`・`tests/README.md`）

`rg attach src/README.md tests/README.md docs/Developer.md CLAUDE.md` の結果は 0 件。

- `src/README.md` の「モジュール一覧」（10〜36 行）に `attach.py`・`attach_handler.py` が無い
- `src/README.md` の 326 行「5 つの `URLSpec` はどれも同じ `{"sd": ..., ...}` を渡す」:
  `AttachHandler` だけは `{"path": ...}` を渡すので、「どれも同じ」は今回の変更で事実と合わなくなった
  （「5 つ」はゴミ箱の経路が足された時点で、すでに合っていなかった）
- `src/README.md` の「Web ハンドラ」のクラス図に `AttachHandler`（`StaticFileHandler` を継承し、`HandlerBase` は継承しない）が無い。
  `HandlerBase.get_template_namespace()` で `attach_store` を渡すようにしたことも書いていない
- `tests/README.md` のテストファイル一覧に `test_attach.py` が無い

`TODO.md` の箇条が名前を挙げているのは `docs/data-format.md` と `README.md` だけなので、範囲に入れるかは main の判断。
`CLAUDE.md` には「構成は `src/README.md`、テストは `tests/README.md` に書く」とある。

### 4. テストが見ていないこと（`tests/test_attach.py`）

- `add`（複製）で、`attach_del` を元の予定に適用しないこと、元の添付を引き継がないこと（`update_attachments()` の `cmd in ["fix", "update"]` の分岐）。
  この分岐を消しても、どのテストも失敗しない（コードを読んで判断した。消して試してはいない）
- 詳細が空で添付だけがある予定で、行が出ること（`sde.html` の `{% if detail or attach_names %}` と「添付 N 件」）
- ファイル名を HTML に出すときのエスケープ。autoescape は全体で有効（`src/README.md` 490 行、テンプレートに `{% autoescape None %}` は無い）なので、
  今は問題が無い。テストで固定していないだけ

それ以外のテストは、壊すと失敗する形になっている:
`_remove_orphan_attachments()` を呼ばない、あるいは残す判定を外すと、ゴミ箱のテスト 3 件のどれかが失敗する。
`parse_url_path()` の検証を外すと、`../../trash.jsonl` は `StaticFileHandler` 自身が 403 にするので、404 を確かめているテストが失敗する。

## 好みの範囲

- `attach.py` の `remove()` は、ファイルが無くても `removed:` のログを出す。実害は無い

## 確信度の低いもの

### 5. 同じ名前で置き直した画像を、ブラウザが古いまま出す場合がありうる（`attach_handler.py`）（実害は未確認）

ETag を出さず、`Cache-Control` も付けない（`StaticFileHandler` は `?v=` が無いと `get_cache_time()` が 0 になる）。
この場合、ブラウザは `Last-Modified` からの経験則でキャッシュしてよい（HTTP の仕様上は、経過時間の 1 割程度）。
長く前に置いた `a.png` を外して、別の `a.png` を置き直すと、同じ URL になる。ブラウザがしばらく古い画像を出すかもしれない。
ブラウザで確かめてはいない。

### 6. ゴミ箱の壊れた行は、版の数に入らない（`trash_handler.py` の `_remove_orphan_attachments()`）（実害は未確認）

`TrashFile.max_version()` は `entries()` を使うので、壊れて読めない行は数えない。
`delete_many()` は、復旧の手がかりとしてそういう行を残す。同じ UUID の行が壊れた形で残っているだけのときは、
フォルダは消える。そうした行を手で直して復旧したときに添付が無い、ということになる。めったに起きない。

## 問題なし

- パス・トラバーサル: `parse_url_path()` は `is_uuid()` と `is_valid_name()` で `/`・`\`・`..`・先頭の `.`・制御文字を弾く。
  そのうえで `StaticFileHandler.validate_absolute_path()` も root の外を拒む。`%2F` は、tornado が `/` に戻したあと
  名前の検証で弾く。`日本語 メモ.pdf`・`a+b%20c#?.txt`・`a&b<c>.png` は、置いて、GET で 200、`remove()` で消える（実測）
- UUID の検証: `uuid_of()` は `SDE_ID_PATTERN`（小文字の UUID と、1 以上の版）を通ったものしか返さないので、`_dir()` の `ValueError` に届く道は無い
- 同じ名前を上書きしない: `open("xb")` と番号の付け直し。書き込みに失敗したら、作りかけのファイルを消す
- 1 つずつ外す: 先に外してから足すので、同じ保存の中で外して同じ名前を置き直しても、元の名前で置ける
- フォルダを消す判定: 版は 1 から始まり（`SDE_ID_PATTERN` は `[1-9][0-9]*`）、`max_version()` は見つからないときだけ 0 を返す。
  そのため `or` による判定で、残っている版を見落とすことは無い。`SchedData.max_version()` は `ToDo.jsonl` も含めて
  全ファイルを読む。「空にする」も `delete_many` と同じ経路を通る（implementer の報告にある。`trash.html` は見ていない）
- 画像以外の扱い: `application/octet-stream`、`attachment`、`nosniff`、`CSP: sandbox`。SVG と HTML は表示させない。
  `mimetypes` は、この環境で png/jpg/JPG/gif/webp/bmp/avif を `IMAGE_TYPES` のとおりに判定した
- `edit.html` を `multipart/form-data` にしたこと: `MainBinder` は `request.files.get("attach", [])` を読むので、
  urlencoded の POST（`nav.js` からの送信と既存のテスト）でも動く。JS の `form.submit()` は enctype をそのまま使う
- `docs/data-format.md`・`README.md`: 置き場所、同名の扱い、空のフォルダを消すこと、ゴミ箱、画像の種類、URL は実装と合っている。
  大きさの上限を `--size-limit` で書いたのは、main の判断のとおり
- データ形式: JSONL は変えていない。`TODO.md` の範囲を超えた変更は無い

## 作り込みすぎ

なし

## 再レビュー（修正 2 回目・3 回目）

対象は、`safe_name()` と `_fit()`、`add()` での番号の付け方、`sched_update.py` の分岐の削除、`src/README.md`・`tests/README.md`、足したテスト。
前回に問題なしとした観点と、範囲外とされた 3 件は見ていない。

### 要修正

無し。

### 検討

#### 7. `docs/data-format.md` に、名前の扱いの変更が反映されていない（184〜186 行）

「ファイル名からはパスの部分と先頭の `.` を除き、制御文字を含む名前は置かない」のままになっている。
今回の修正で、次の 2 つの挙動が加わったが、どちらも書かれていない。

- 先頭の空白も除く（末尾の空白も除く）
- UTF-8 で 255 バイトを超える名前は、拡張子を残して縮める（番号を付けた名前も 255 バイトに収まる）

`rg -n "255|縮め" docs/data-format.md README.md` の結果は 0 件。

### 問題なし

- 前回の要修正 1（先頭が `.` と空白の名前）: 直っている。スクラッチパッドのスクリプトで、20 万件余りのランダムな名前を調べた
  （`.`・半角と全角の空白・`あ`・`é`・タブなどを組み合わせたもの、および `x*300+". "` などの境目の名前）。
  `safe_name()` を 2 回通して変わらないこと、255 バイト以内であること、
  `_fit(r, 1)`・`_fit(r, 12345)` が `is_valid_name()` を通り、255 バイト以内で、元の名前と違うことを確かめた。反例は 0 件だった
- 前回の検討 2（長すぎる名前）: `_fit()` で縮める。`MAX_SUFFIX_BYTES` で、長い拡張子のときに `room` が負にならないようにしている
- 前回の検討 4 と、分岐の削除: `add` のときに `attach_del` を当てる先は、`new_id()` が作った新しい UUID のフォルダで、まだ無い。
  そのため `remove()` は何もせずに戻る（`unlink(missing_ok=True)`、`rmdir` の `OSError` は抑える）。
  `del` は `new_sde` が無いので `update_attachments()` を呼ばない。docstring はこの挙動と合っている。
  `test_add_copy_keeps_original_attachments` は、元の添付が残り、新しい UUID には送ったファイルだけがあることを見ている
- 足したテスト: 長い名前のテストは、同じ名前を 2 つ送るので、番号を付けたときの縮め方も通る（`len(names) == 2` で、2 つが違う名前になることも見ている）。
  ドットと空白のテストは、置く・開く・外すを Web 経由で通している
- `src/README.md`: モジュール一覧、`URLSpec` の記述、クラス図、`HandlerBase`・`AttachHandler` の箇条は、コードと合っている
  （`AttachHandler` の継承、`parse_url_path()` の 404、`IMAGE_TYPES`、`{"path": ...}`）。mermaid の描画は見ていない（verifier が見る）
- `tests/README.md`: `test_attach.py` の説明は、テストの中身と合っている

### 作り込みすぎ

なし
