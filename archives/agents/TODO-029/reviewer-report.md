# TODO-029 reviewer の報告

`git diff`（未コミット）と `TODO.md` の TODO-029 節、implementer の報告を
読んだ。**src/ の 4 ファイルの変更には、正しさの問題を見つけられなかった。**
判断 2 点はどちらも妥当だと考える（根拠は下記）。指摘は**テストと文書**に
3 件、うち 1 件は「常に通るアサーション」で確信度が高い。

## 依頼された判断 2 点についての見立て

### 判断 1: `\r` を `migrate.py` の `conv_file()` 側で落としたこと

**妥当。** 理由は 3 つ。

- `split_lines()` は `.jsonl` の読み込みでも使われ、飛ばした行は生の
  バイト列のまま `skipped_lines` に入って `save()` が書き戻す
  （`docs/data-format.md`「壊れた行の扱い」）。ここで `\r` を落とすと、
  読み込み側の仕様を書き直すことになる。implementer の理由づけのとおり
- 落とす位置（`is_empty_line()` と `decode_line()` の**前**）も正しい。
  CRLF・行末に改行が無い場合・`\r\n` で終わるファイル・`\r` だけの行の
  4 通りを追ったが、どれも `\r` が残らず、空行の数え方も変わらない
- 変換できなかった行を書き出す `error_lines` にも `\r` の落ちた行が入る。
  こちらも旧形式に合う

**行の途中の `\r` を残す扱いについて。** 実害はまず出ないと考える。
CRLF のファイルを `b"\n"` で切れば `\r` は行末にしか現れず、途中に
`\r` が残るのは「detail に単独の CR が入っている」場合だけ。ただし
その場合、旧実装（テキストモードの `readlines()`）では**その `\r` で行が
割れていた**ので、どのみち今回の移行とは結果が違う。TODO-029 の範囲
（行末）を超える話で、手を出さなかった判断でよい。

### 判断 2: `search_str` も `Conf.cgi` へ正規化後を保存すること

**妥当。** 照合される側（`SchedDataEnt.search_str()`）が `normalize()`
済みで、`filter_str` は TODO-028 で既に「変換後を保存」に揃っている。
`search_str` だけ「保存は打ったまま・表示は小文字」で食い違っていた方が
説明しづらい。利用者から見て**新たに失われるもの**も無い
（大文字は TODO-021 の時点で既に画面上は小文字になっていた）。

テストの書き直し方も妥当。落ちた 1 件
（`test_search_str_is_saved_as_is_and_shown_lowered`）は、旧挙動そのものを
固定していたテストなので、書き直す以外に選択肢が無い。docstring に旧挙動を
残してあるのもよい。

**確認したが問題なかった点:**

- `get_conf_arg()` の空文字の扱い（TODO-028 の「絞り込みの解除」）は
  変わらない。`normalize("")` は `""` で、`converted is not None` を通る
- `filter_str` の `!`（否定）の判定は `normalize()` のあとだが、
  `normalize()` は `!` を触らないので影響なし
- 既に `Conf.cgi` に入っている正規化前の値は、読むときに `normalize()` を
  通るので当たり方は変わる（意図どおり）。書き戻しはされない
- `search_str` を受け取る他の経路（`sde.html` → `EditHandler` →
  `edit.html`）は `sde_align` の判定にしか使っておらず、影響なし

### 参考: `orig_date`（依頼外だが読んだ）

`EditHandler` 側は、既存の行については `orig_date = sdf.date` が
`get_sdf(date)` の `date` と必ず一致するので、実質「ToDo なら `None`、
それ以外は表示している日付」になる。これが TODO-029 の直したかった
ところ（旧: `sde.date`）で、正しい。新規のとき `date` にしたのも、
`None` にすると `cmd_del(None, …)` が `ToDo.jsonl` を開いて `.bak` まで
作る道が開くので、判断として妥当。

`MainHandler.exec_cmd()` 側は下の「確信度が低いもの」に書く。

---

## 指摘（確信度が高いもの）

### 1. `tests/test_migrate.py::test_crlf_line_has_no_cr` の最後の assert は、常に通る

```python
assert all("\r" not in json.dumps(d) for d in data)
```

`json.dumps()` は CR を **`\r` の 2 文字（バックスラッシュ + r）へ
エスケープする**ので、`d` の値に CR が入っていても、返る文字列に CR の
文字そのものは決して現れない。実測:

```
>>> json.dumps({"detail": "x\r"})
'{"detail": "x\\r"}'   # CR は含まれない
```

つまりこの行は、`migrate.py` の変更を戻しても通る。実装を戻したときに
落ちるのは 1 つ上の `data[0]["detail"] == "議題\n・進捗"` と
`data[1]["detail"] == ""` の 2 行だけで、テストとしては成立しているが、
**最後の 1 行は読む人に「全フィールドを見ている」と誤解させる**。
値そのものを見る形（例: `d.values()` の各文字列に CR が無いこと）にするか、
消すのがよい。

同じ理由で、implementer の報告にある
「`.jsonl` に `\r` が 1 つも入らない（`od -c` で確認）」も、確認に
なっていない（CR はファイル上でも `\r` の 2 文字にエスケープされるので、
不具合があっても `od -c` に CR は出ない）。**修正自体は
`detail` の値を見る assert で担保されている**ので、直すべきは確認の
書き方であって、実装ではない。

### 2. `test_crlf_empty_line_is_skipped` は、変更前でも通る

`is_empty_line()` は `raw_line.strip()` なので、`b"\r"` は
`removesuffix(b"\r")` の有無にかかわらず空行と判定される。implementer 自身も
報告で「数え方は変わらない」と書いていて、テストの内容としては正しいが、
**TODO-029 の変更を守るテストではない**（`removesuffix()` を消しても通る）。
残すなら「挙動が変わっていないことの確認」と分かるようにしておきたい。

### 3. `src/README.md` の `orig_date` の説明に、新規のときの分岐が無い

```
フォームの隠しフィールド orig_date … は、テンプレートではなく handler が
決める ＝ その sde を読み込んだファイルの日付（ToDo は None。TODO-029）
```

実際には**新規（`sde_id` 無し）のときは表示している日付**で、まだどの
ファイルにも入っていない。`edit_handler.py` のコメントには書いてあるので、
README だけ落ちている。新規のときの値は「`None` にしない」という判断が
入っているところなので、1 文足しておきたい。

---

## 確信度が低いもの（判断は main に任せる）

### A. `MainHandler.exec_cmd()` の `orig_date` は、実質的に挙動が変わらない

`orig_date = modified_date` は、旧コードのテンプレート側
（`sde.date`、ToDo なら `None`）と**必ず同じ値になる**と読んだ。理由:

- `cmd_add()` は `self._sd.add_sde(new_sde.date, new_sde)` と、
  行の `date` と同じファイルへ書く（ToDo は `None`）
- `exec_update()` は書いたあとの `new_sde.date`（ToDo なら `None`）を
  `modified_date` として返す
- `get_modified_sde()` はその `modified_date` のファイルから読み直す

つまり `cmd=update` の直後は、行の `date` とファイルの日付が必ず一致する。
**変更は無害で、テンプレートから handler へ寄せる意味はある**が、
コメントの「次の更新・削除が、その行が実際に入っているファイルへ届く
ようにする」は、この経路に限れば言い過ぎ。`cmd=update` 経路の
`orig_date` を見るテストが無いのも、この読みと整合している
（no-op なので足しても変更前から通る）。**足すべきかどうかは main の判断**。

### B. `sde.html` の `orig_date` は、誰も読んでいない

`sde.html` の 10・15 行目で `orig_date` を組み立てて、93 行目で
`doPost()` のパラメータに載せているが、**`EditHandler.get()` は
`orig_date` 引数を読んでいない**（今回の変更前からそう）。ToDo のときは
`'{{ None }}'` が文字列 `"None"` として送られる。今回の変更で
「`orig_date` は handler が決める」と方針が定まったので、送る側の
死んだコードが残っているのは紛らわしい。**TODO-029 の範囲外**なので、
直すなら別項目。

### C. TODO.md の「据え置き 2 点」の扱い

- `get_conf_arg()` の保存方針は、**コードは変わっていない**
  （`isinstance(converted, str)` で実行時に決める設計はそのまま）。
  文字列を返す変換がすべて「変換後を保存」に揃ったのは事実なので、
  implementer の「実質的に片付いている」は挙動の話としては正しいが、
  TODO に書かれた「設計の見直し」そのものはしていない。
  **見直し済みとして閉じるかどうかは main の判断**
- `date2path()` の `expanduser()` が 2 か所に分かれている件は、
  手つかず（implementer も報告に明記）

---

## 見つからなかったもの（確認した範囲）

- `edit.html` から `{% set orig_date = … %}` を消したことによる
  未定義変数の危険: `HTML_EDIT` を描くのは `EditHandler.get()` と
  `MainHandler.exec_cmd()` の 2 か所だけで、どちらも `orig_date` を
  渡している
- `normalize()` を通したことによる照合側とのずれ:
  `filter_match()`/`search_match()` はどちらも `sde.search_str()`
  （`normalize()` 済み）に対して照合しており、両側が揃っている
- 例外の握り潰し・黙って失敗する書き方: 今回の差分には無い
- `docs/data-format.md` の記述と実装のずれ: 「4 か所」の数え方
  （重要/取り消しの判定・並べ替えのキー・検索の照合対象・入力文字列）は
  コードの `normalize()` の呼び出し箇所と合っている
