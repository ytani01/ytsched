# TODO-006 reviewer 報告

型ヒントの整備（未コミットの作業ツリー、4 ファイル）のレビュー。
`git diff` の全差分と、関連する呼び出し箇所・テンプレートを読んだ。
テスト実行と起動確認はしていない（verifier の担当）。

結論から言うと、**依頼で名指しされた 4 点（`__init__` の 1 文化、
`todo_flag`、`time_start`/`time_end` の `None` 化、
`exec_update()`／`add_sde()`／`_sdf_cache`）は、いずれも挙動を
変えていない**か、変わっても妥当だと確認できた。根拠は「4. 確認した
こと」に書く。

指摘は 2 件（うち 1 件は挙動の変化を伴うもの）。

---

## 1. 確信度の高い指摘

### 1-1. `main_handler.py:147-151` — 500 になっていた経路が、黙って通るようになった

```python
todo_flag = False
if sde is not None:
    todo_flag = sde.is_todo()
    if todo_flag:
        modified_date = sde.date
```

`get_sde()` が `SchedDataEnt | None` になったための guard 自体は必要。
問題は **`sde is None` のときに何も言わずに先へ進む**こと。
変更前は `sde.is_todo()` が AttributeError を投げて 500 になっていた。

**到達する入力がある。**「`date` が空の POST で、ToDo ではない予定を
`cmd=add`（または `fix`/`update`）する」場合:

1. `exec_update()`:445-450 で `date_str` が空 → `date = None`
2. `cmd_add()` は `new_sde.is_todo()` が偽なので
   `self._sd.add_sde(date, new_sde)` = `add_sde(None, new_sde)` を呼ぶ
   → `get_sdf(None)` なので、**ToDo ではない予定が `ToDo.cgi` に書かれる**
3. `SchedDataEnt.__init__` は `date=None` を今日に置き換えるので
   `new_sde.date` は今日。ToDo ではないため `exec_update()` は
   `date = new_sde.date`（＝今日）を返す
4. 呼び出し側 137-144 行で `get_sdf(今日)` → 今日のファイルには無いので
   `sdf.get_sde(modified_sde_id)` が `None`

変更前はここで 500（＝おかしいことが分かる）。変更後は
`cmd=add`/`fix` なら**そのまま通常の一覧画面が 200 で返り、予定が
`ToDo.cgi` に紛れ込んだことに気づけない**。

`date` 入力は `edit.html:229-231` で `value="{{ sde.date }}"` と必ず
埋まるので通常操作では起きないが、`type="date"` の入力は手で空に
できるため、ブラウザ上で日付を消せば到達する。ToDo だった項目の
`sde_type` から `□` を外して保存する操作でも同じ経路に入る。

なお `cmd=update` のときは `sde=None` のまま `edit.html` を render し、
テンプレート 5 行目の `{% set orig_date = sde.date %}` で結局落ちる
（500 の発生位置がハンドラからテンプレートへ移るだけ）。

**根本原因（`date` が空のとき ToDo ファイルへ書く）は TODO-006 より
前からあるもので、この項目の範囲外。** ここで指摘したいのは、
型の整備のついでに**失敗が黙って隠れる形になった**点だけ。
最低限 `else: self._mylog.warning(...)` を入れるか、guard を入れずに
`assert` にしておくか、main の判断を仰ぎたい。

### 1-2. `ytsched.py:588` — クラス docstring がキャッシュのキーの型と食い違ったまま

`_sdf_cache` の型注釈は `datetime.date | None` に直り、618 行に
「ToDo は `date` が None のキーで扱う」というコメントも足された。
一方 `SchedData` のクラス docstring（578-591 行）は

```
    date1, date2, .. : datetime.date
```

のままで、ここだけ実体と合っていない。注釈より先に読まれる場所なので、
`datetime.date | None`（None は ToDo）に直しておくのがよい。
挙動には影響しない。

---

## 2. 確信度が低い（気になる程度）

以下は**指摘というより申し送り**。今回の変更が原因ではないもの、
好みの範囲のものを分けて置く。

### 2-1. `add_sde()` だけ既定値が無くなり、兄弟メソッドと不揃い

`SchedData` の `get_sde(date=None, sde_id="")` /
`del_sde(date=None, sde_id="")` は既定値付きのまま、`add_sde` だけ
`(self, date, sde)` になった。ただし `sde` の既定値を外す以上、
その前にある `date` の既定値も外すしかない（Python の構文上、
既定値付きの後ろに既定値無しは置けない）。keyword-only にする手も
あるが差分が増えるので、**実装者の選択 (c) が妥当**だと考える。
不揃いが気になるなら、docstring に「`date=None` は ToDo」と
明記されているので実害は無い、という整理でよいと思う。

### 2-2. `edit_handler.py:95` の `sde` も `None` になりうる（今回の変更とは無関係）

`sde = sdf.get_sde(sde_id)` は、存在しない `sde_id` を URL/引数で
渡されると `None` を返し、`edit.html:5` の `sde.date` で落ちる。
戻り値型が `| None` になって実体は正しく表現されたが、`render()` は
型が付いていないので型チェッカーは何も言わない。
**TODO-006 の範囲外**（`EditHandler.get()` の型注釈と同じく意図的に
残した部分）。別項目にするなら 1-1 と一緒に「`sde` が見つからない
ときの扱いを決める」でまとめられる。

### 2-3. `type_is_todo(sde_type: str | None)`

本体を `str | None` に広げた判断（実装者の判断 5）は、
`tests/test_ytsched.py:250-251` の `test_type_is_todo_none` が
意図して `None` を渡していること、本体が `if sde_type:` で弾いて
いることから妥当。ただし**呼び出し側（`main_handler.py:531` の
`SchedDataEnt.type_is_todo(sde_type)`）は必ず `str` を渡す**ので、
実質はテストのためだけに広げた形になっている。今の書き方で問題は
無いが、そういう性質のものだと認識しておきたい。

---

## 3. 指摘しなかったもの（既知として依頼にあったもの）

- `__class__` の 2 件（TODO-007）
- ruff の 87 件（TODO-015 / TODO-008）
- `EditHandler.get()` と `handler.py` の型注釈が無い件
- `EditHandler.get()` の `todo_flag` 引数が本文で無条件に上書き
  される件（実装者が「挙動を変えない」ため触っていないと明記済み）

---

## 4. 確認したこと（依頼の 4 点）

### 4-1. `SchedDataEnt.__init__` の代入を 1 文にまとめた件 — 問題無し

```python
self.sde_id = sde_id if sde_id else SchedDataEnt.new_id()
self.date = date if date is not None else datetime.date.today()
```

- 条件式なので `new_id()` は `sde_id` が falsy のときだけ評価される。
  旧 `if not self.sde_id: self.sde_id = SchedDataEnt.new_id()` と
  判定条件（falsy）も完全に同じ。`None` / `""` のどちらでも同じ結果
- `new_id()`（`ytsched.py:214-218`）は `uuid.uuid4()` と
  `cls._mylog.debug()` だけで、**インスタンス属性を一切読まない**。
  `cls._mylog` は `__init__` の 118-119 行、つまり移動前・移動後の
  どちらの呼び出し位置よりも前で設定済み。したがって、旧位置
  （`__init__` 末尾）と新位置（先頭寄り）で結果は変わらない
- 呼び出し元の `SchedDataEnt` は継承されておらず、`new_id()` の
  上書きも無いので、`SchedDataEnt.new_id()` という明示の書き方
  （これは変更前からそのまま）による差も無い
- `self.date` は `if date is not None` で、旧 `if self.date is None` と
  完全に等価
- 変わるのは **debug ログの出力順だけ**（`new_id` の行が
  `SchedDataEnt.__init__` の他のログより前に出る）

`edit_handler.py:96` の `SchedDataEnt("", date, debug=...)` も
従来どおり新 ID になることを確認した。

### 4-2. `edit_handler.py:77` の `todo_flag` — 挙動は同じ

```python
todo_flag_str = self.get_argument("todo_flag", "")
todo_flag = todo_flag_str == "true"
```

- tornado の `RequestHandler._get_argument` は、引数が無いとき
  `default` が `_ArgDefaultMarker` でなければ**そのまま返す**。
  `False` も `""` も marker ではないので、返る値が `False` → `""` に
  変わるだけ
- 直後の比較は変更前も `== "true"` で、`False == "true"` も
  `"" == "true"` も `False`。**引数が無ければ `todo_flag = False`** で同じ
- 引数があるときは `args[-1]`（`str`）が返るので `default` は無関係
- 変更前後とも `todo_flag` に入るのは `True` / `False` の bool

実装者の判断 4 の説明は正しい。**指摘無し。**

### 4-3. `time_start` / `time_end` の `''` → `None` — 影響を受ける箇所は残っていない

`time_start` / `time_end` の**全参照**を洗った（`src` の `.py` と
`webroot` 配下の全ファイル、`tests`）。値を読んでいるのは次だけで、
**すべて `if ...:` の真偽判定で囲われている**:

| 場所 | 内容 |
| --- | --- |
| `ytsched.py:152-158` | `__str__` |
| `ytsched.py:176-181` | `mk_dataline()` |
| `ytsched.py:320-325` | `get_timestr()`（`get_sortkey()` から使われる） |
| `templates/sde.html:26,31` | `strftime()` を `if` で囲っている |
| `templates/edit.html:14,18,241,245` | 同上（`str(sde.time_start)` も `if` の中） |

- **比較・連結・書式化に生値を使っている箇所は無い**
  （`== ""` や `"%s" % sde.time_start` の類は 0 件）
- `main_handler.py:494-504, 539-545` は**元から `None` を作っていた**
  （`else: time_start = None`）。つまり Web 経由の予定には以前から
  `None` が入っており、`''` が入るのは `load()` 経由だけだった。
  今回の変更で両者が `None` に揃った形で、むしろ一貫性は上がっている
- `datetime.time(0, 0)` は Python 3.5 以降 truthy なので、
  「0 時ちょうど」の予定でも判定は変わらない（`''` 時代と同じ）
- `SchedDataFile.load()` の `time_start2` / `time_end2` は
  `SchedDataEnt(...)` に渡すだけで他に参照が無い
- `webroot` の js/css には `time_start` / `time_end` の参照は無い
  （`sde.html:90` の `todo_flag:` のみ）

出力（`mk_dataline()` の `:-:` / `HH:MM-:` など）も変わらない。
**指摘無し。**

### 4-4. `exec_update()` / `add_sde()` / `_sdf_cache` — いずれも妥当

**`exec_update()` の戻り値 `tuple[datetime.date | None, str | None]`**:
実体と合っている。`date` は 462 行で `None` 初期化、`date` 引数が無ければ
`None` のまま返る。587-588 行で ToDo なら明示的に `None`。
`modified_sde_id` は 562 行で `None` 初期化、`cmd == "del"` では
`cmd_add()` を通らないので `None` のまま。呼び出しは 137 行の 1 か所
だけで、受けた値は `get_sdf()` と `get_sde()` に渡すが、どちらも
`| None` を受けるようになった。docstring も実体に合っている。
**依頼の `tuple[datetime.date, str]` より、こちらが正しい。**

**`add_sde()` の既定値を外した件**: 呼び出しは
`main_handler.py:635,637` と `tests/test_ytsched.py:704,712,720` の
5 か所で、**すべて 2 引数の位置引数**。キーワード呼び出しは無い
（`sdf.add_sde(sde)` の形は `SchedDataFile.add_sde`（引数 1 個）で、
こちらは今回変更していない別メソッド）。
旧 `sde: SchedDataEnt = None` は、`None` で呼ぶと
`SchedDataFile.add_sde()` の `sorted(key=x.get_sortkey)` で
AttributeError になる**意味の無い既定値**だったという説明も正しい。
実行時の振る舞いを足さずに型を正す方法として (c) が妥当。
（上記 2-1 の不揃いだけ残る。）

**`_sdf_cache` のキーを `datetime.date | None` にした件**: 正しい。
`get_sdf(None)` は `main_handler.py:280`（ToDo 一覧）と
`edit_handler.py:91`（ToDo の編集）で実際に使われており、
`SchedDataFile.__init__` の docstring にも「None: ToDo」とある。
TODO-004 で入った `datetime.date` のほうが実体と合っていなかった。
（docstring の食い違いだけ 1-2 に挙げた。）

---

## 5. その他、差分を読んで確認した点

- `main_handler.py:209-222` の `todo_days_str` / `todo_days_value` 分離:
  値は変わらない。`self.DEF_TODO_DAYS`（= `365`、`int`）を
  `str()` してから `int()` に通すので結果は同じ。
  `set_conf()` に渡すのも従来どおり引数の文字列そのまま。
  非数値が来たときに `int()` が ValueError を投げるのも変更前と同じ
- `main_handler.py:556` の `sde_id: str | None = self.get_argument("sde_id")`:
  既定値なしの `get_argument` なので、引数が無ければ従来どおり
  `MissingArgumentError`。注釈を足しただけで挙動は変わらない
- `tests/test_ytsched.py:28` の `dict[str, Any]`: `**param` で渡す
  用途なので `Any` が適切。テストの意図は変わっていない
- `tests/test_ytsched.py:696-699`: `assert sde is not None` を挟んだだけで、
  確かめている内容は同じ。テスト関数の増減無し
- 新規・削除ファイル無し、データ形式に関わる出力の変更無し
