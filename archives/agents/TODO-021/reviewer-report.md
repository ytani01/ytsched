# TODO-021 reviewer の報告 — 挙動が変わっていないかのレビュー

対象: `git diff src/`（`__main__.py` / `handler.py` / `main_handler.py` /
`ytsched.py`）。テストの実行・起動確認はしていない（verifier の担当）。

## 結論

**挙動が変わる指摘は無し。** 依頼の 7 点と、implementer(2) が単独で決めた
判断 3 件をすべて追ったが、元と結果が食い違う入力を見つけられなかった。

確実に差が出るものが 1 件だけある（**debug ログの量**。C-1）。挙動では
ないので、直すかどうかは main の判断。

---

## 1. 確信度の高い指摘

### C-1. `is_todo()` を呼ぶたびに debug ログが出るようになった

`src/ytsched/ytsched.py:256-259`

```python
def is_todo(self):
    # self.__log.debug("")      ← 元はコメントアウトされていた
    return self.type_is_todo(self.type)
```

委譲先の `type_is_todo()`（`ytsched.py:245`）には
`cls.__log.debug(f"sde_type={sde_type}")` が**生きている**。元の
`is_todo()` は debug を意図的にコメントアウトしてあったので、
**`is_todo()` 経由のログが 0 行から毎回 1 行に増えた**。

問題になる状態: `--debug` でサーバを動かしたとき。`sde.html` は 1 件の
予定につき `sde.is_todo()` を最大 5 回呼ぶ（`sde.html:14,37,71,90,96`）
ので、45 日ぶんの一覧に 100 件あれば **1 リクエストで数百行**増える。
`mylog.py` の水準は `_filter` で落とすが、**f-string の組み立てと
loguru のレコード生成は水準に関係なく毎回走る**ので、既定の INFO でも
費用だけはかかる（画面には出ない）。

TODO-021 の C（`is_todo()` を `type_is_todo()` へ委譲）をやると必ず
こうなるので、実装の誤りというより**委譲したときに一緒に決めるべき点**。
直すなら `type_is_todo()` 側の debug を落とす（既存の呼び出し 1 か所
`main_handler.py:758` のログが消える）か、`is_todo()` の委譲をやめる。

---

## 2. 追った結果、差が無いと確認したもの

依頼の 7 点と追記の 3 件。**指摘ではなく、確認した根拠の記録**。

### 2-1. 設定値の取り出し 4 か所（依頼 1／追記 1）

`main_handler.py:284` の
`if value is not None and (empty_is_given or value):` は、
4 か所とも元と一致する。

| 呼び出し | `empty_is_given` | 展開すると | 元の条件 |
| --- | --- | --- | --- |
| `search_str` | `True` | `value is not None` | `search_str is not None` |
| `search_n` | `True` | `value is not None` | `search_n_str is not None` |
| `todo_days` | `False` | `value is not None and value` | `if todo_days_str:` |
| `filter_str` | `False` | 同上 | `if filter_str:` |

- `value` は `str | None` しか取らない（`get_argument(name, None)`）。
  `None` のとき `bool(None)` は偽なので、`value is not None and value` は
  `bool(value)` と同値。**`0` や `[]` のような「`None` でないのに偽」の
  値が来る経路が無い**ことを確かめた
- `filter_str` の既定値が `""` → `None` に変わった件も、truthy 分岐なので
  `""` と `None` の行き先が同じ（どちらも `elif conf_value:` へ落ちる）
- **保存の副作用も元のまま。** `set_conf()` は「値が渡された」枝の中で
  `value != conf_value` のときだけ呼ばれ、`.lower()` と `int()` は
  呼び出し側に残っている。したがって
  - 空の `search_str` → `SearchStr\t\n` が保存され、検索モードから抜ける
  - 空の `filter_str` → `Conf.cgi` に触らず、保存済みの値が効き続ける
  - 空の `search_n` → `SearchN\t\n` の保存だけ先に済んでから `int("")`
    で 500
  - 空の `todo_days` → 何も保存せず既定値
  という**元の食い違いがそのまま残っている**
- **4 か所を呼ぶ順序も、`get_conf()` → `get_argument()` の順も変わって
  いない**（`Conf.cgi` はキーの追加順に書き出すので、順序が変われば
  ファイルの中身が変わる）

### 2-2. `search_match()`（依頼 2）

元は 3 か所とも
`if search_re is not None and not search_re.search(sde.search_str()): continue`
で、まったく同じ形だった（旧 322 / 374 / 385 行）。新しい
`search_match()`（`main_handler.py:686`）は `search_re is None` で `True` を
返すので、`if not self.search_match(...): continue` は
`search_re is not None and not search_re.search(...)` と同値。
**`search_re is None` のとき絞り込まない**という意味は保たれている。

`filter_match()` と並びが揃っており、`load_todo()` の中で
`filter_match()` → `search_match()` の順である点も元のまま。

### 2-3. 一覧を集めるループ（依頼 3／追記 2）

`load_sched()`（`main_handler.py:576-636`）は、`date_from` / `date_to` の
初期化、`search_mode` のときの上書き、`while date1 > date_from:`、
2 つの打ち切り（`search_count >= search_n`、`date1 <= date_from1`）と
そこでの `date_from = date1`、`sched[::-1]` まで元と一文字も違わない。
**書き換わった `date_from` は戻り値で返し、`get()` がそれを `render()` へ
渡している**ので、テンプレートに届く値は同じ。`date_to` はループ内で
変わらないので、返し方に関係なく同じ。

`delta_day1` → `MainHandler.DELTA_DAY1` も安全。`timedelta` は
immutable で、テンプレート側の使い方（`main.html:209` の
`date_to - date_from + delta_day1`、`sde.html:20` の `delta_day1 * 7`）は
どちらも新しいオブジェクトを作るだけなので、共有しても壊れない。

`date_from1` が `if search_mode:` の中でしか代入されない（未定義になり
得る）構造も**元のまま**で、参照は `if search_mode and search_count > 0:`
の中だけ。増やしても減らしてもいない。

### 2-4. `cmd == "update"` の経路（依頼 4）

`exec_cmd()`（`main_handler.py:294-352`）の分岐は元と対応が取れている。

| 元 | 新 |
| --- | --- |
| `cmd` が 4 つのどれでもない | `return None, None, False`（`modified_date`/`modified_sde_id` が `None` のまま先へ進むのと同じ） |
| `cmd == "del"` | `return modified_date, modified_sde_id, False`（元も `sde` の読み直しを飛ばし、`update` でもないので素通り） |
| `cmd == "update"` | `render()` してから `rendered=True` を返し、`get()` が `return`。**その先へ落ちない** |
| `add` / `fix` | `todo_flag` なら `modified_date = sde.date`、`rendered=False` |

`render()` に渡す 10 個の引数（`date=modified_date`、`sde`、
`new_flag=False`、`todo_flag`、`search_str`）も元と同じ。`search_str` は
`get()` で `.lower()` 済みのものが渡る点も元のまま。

### 2-5. `exec_update()` の ToDo 完了時の補正（依頼 5／追記 5）

走る条件 `if deadline_date_str and not SchedDataEnt.type_is_todo(sde_type):`
（`main_handler.py:758`）は式ごとそのまま。`fix_todo_done()` の中身も
`date = today`、`time_start` の秒切り捨て、`time_end = None`、
`〆{deadline_date} {start}{end}\n{detail}` まで元と同じで、
`deadline_date_str.replace("-", "/")` と、`deadline_time_end` が空でない
ときだけ `-` を前置する処理（`get_deadline_str()` 側）も動いていない。
**4 つの戻り値の受け側の並びも `date, time_start, time_end, detail` で
合っている**（入れ替わりは無い）。

`get_date_arg()` / `get_time_arg()` も、元の
「引数が truthy なら `fromisoformat()`、でなければ `None`」と同値。
`cmd_add()` の位置引数 8 つの並びも変えていない
（implementer(1) の `test_deadline_fixes_date_and_time_start` が
これに依存している）。

### 2-6. `ytsched.py` の共通化（依頼 6／追記 3）

- `title_starts_with()`: `normalize(self.title).startswith(tuple(...))`。
  元にあった `if self.title == "": return False` を落としても、
  `"".startswith(prefix)` は**どの接頭辞も空文字でない限り**必ず偽。
  `TITLE_PREFIX_IMPORTANT`（5 個）・`TITLE_PREFIX_CANCELED`（7 個）に
  空文字が無いことを目視で確認した（`ytsched.py:57-72`）。
  `self.title` が `None` になり得ないことも
  `__init__` の `if not self.title: self.title = self.TITLE_NULL` で
  確認（元の実装も `None` なら `normalize()` で落ちていたので、
  そこも同じ）
- `get_timestr()`: `time2str()` は `None` のときだけ `None`、それ以外は
  必ず `"HH:MM"`（長さ 5 の文字列＝truthy）を返すので、`or ":"` は元の
  `if self.time_start:` と同じ枝を選ぶ。`datetime.time(0, 0)` は
  Python 3.5 以降 truthy なので、元の truthy 判定と `is not None` の
  差も出ない（`00:00` は元も新も `"00:00"`）
- `is_todo()` の委譲: 返す値は元と同じ（C-1 はログの話だけ）
- `load()` の `out2` 削除は戻り値が同じ

### 2-7. `__main__.py` の `end()` 削除（依頼 7）

削除した `DataFileApp.end()` は `self.__log.debug("")` 1 行だけで、
呼び出しも `x_data1()` の `finally` の 1 か所（`git grep` で他に無いことを
確認）。`try` / `finally` と `_log.debug("finally")` /
`_log.info("end")` は残っているので、**例外が出たときも `end` の
info は今までどおり出る**（`app.main()` が投げても `finally` は走る）。
`DataFileApp` の生成前に例外が出たら元も `app.end()` に届いていない。

### 2-8. `handler.py`（TODO-021 の D）

- `get_conf()` の `try/except KeyError` → `self._conf.get(name)`。
  `_conf` は `load_conf()` が返す `dict[str, str]` だけなので同値
  （`None` を返す点も同じ）
- `__init__` の 8 つの代入は明示のまま。まとめたのは debug ログだけで、
  読む値・順序・`_conf_file` の作り方は変わっていない

### 2-9. 既存テストの書き換え

`git diff --numstat tests/` は `test_handler.py` の `+21 / -1` のみ。
`-1` は `from helpers import ...` に `URL_PREFIX` を足した行で、
**既存のテスト本体は 1 行も書き換わっていない**。
`tests/test_main_handler.py` は新規（未追跡）。

---

## 3. 確信度は低いが、気になったところ

いずれも**挙動は変わっていない**。直すかどうかは main の判断。

### L-1. 「ついでに揃えた」箇所が 1 つある（値は同じ）

`main_handler.py:800`（`fix_todo_done()`）で、元の `"%H:%M"` 直書きが
`SchedDataEnt.TIME_FORMAT` になっている。`TIME_FORMAT` の値は `"%H:%M"`
なので結果は同じで、implementer(2) も報告の「単独で決めた判断 5」で
申告している。TODO-021 の C に挙がっていた指摘を B の範囲へ広げた形なので、
**範囲を超えたと見るなら差し戻す余地がある**（実害は無い）。
なお、この定数は `to_dict()` / `time2str()` でも使われており、
`"%H:%M"` の直書きは `src/` に残っていない。

### L-2. `load_sched()` の引数 9 個

`main_handler.py:552-568`。implementer(2) も申告済み。減らすには
リクエスト単位の状態を `self` に持たせるか、まとめ役の型を作ることに
なり、「挙動を変えない」範囲を超える。**この項目では触らないのが
正しい**と考えるが、`filter_re` / `filter_neg` / `search_re` /
`search_mode` / `search_n` の 5 つは「今回の検索条件」という 1 つの
かたまりなので、別項目にする価値はある。

### L-3. `exec_cmd()` が描画も担っている

`main_handler.py:294`。名前は「コマンドの実行」だが、`cmd == "update"`
のときだけ `render()` まで済ませ、3 つ目の戻り値でそれを知らせる。
docstring に明記してあるので読み違えにくいが、
**`get()` 以外から呼ぶと二重描画になる**造りではある。
今は呼び出しが `get()` の 1 か所だけなので実害は無い。

### L-4. `title_starts_with()` が呼ばれるたびに `tuple()` を作る

`ytsched.py:280`。`ClassVar[list[str]]` を毎回タプルに変換している。
一覧 1 件につき `is_important()` と `is_canceled()` が呼ばれるので
回数は多いが、要素は 5〜7 個で費用はごく小さい。
クラス側を最初からタプルにすれば消えるが、それは C の範囲を超える。

---

## 4. 見なかったもの

- `tests/` の差分（足場のテスト。依頼で対象外）
- 変数名の趣味・コメントの多寡・行長
- `TODO.md` が「別項目にする」と書いている事柄
  （4 か所の条件を揃える、空の `search_n` で 500、
  `year`/`month`/`day` の検証、`sde_align` が保存されない、
  `COOKIE_TODO_DAYS` が未使用）
