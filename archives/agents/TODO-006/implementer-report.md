# TODO-006 implementer 報告

型ヒントの整備。`time_start` / `time_end` の `''` → `None` 化、
implicit Optional の明示、`-> (datetime.date, str)` の修正、
mypy / basedpyright のエラー解消。

## 変更したファイル

- `src/ytsched/ytsched.py` — 型注釈の追加・修正が中心。`''` → `None`
- `src/ytsched/main_handler.py` — `todo_days` の変数分離、戻り値型、
  `sde_id` の注釈、`get_sde()` が `None` を返すようになった件の対応
- `src/ytsched/edit_handler.py` — `get_argument('todo_flag', False)` の修正
- `tests/test_ytsched.py` — 本体の型が厳しくなって出た 2 か所

新規作成・削除したファイルは無い。

## 1. 直した箇所の一覧

行番号は**変更後**のもの。

### `src/ytsched/ytsched.py`

| 行 | 変更前 | 変更後 |
| --- | --- | --- |
| 107 | `sde_id=None` | `sde_id: str \| None = None` |
| 108 | `date: datetime.date = None` | `date: datetime.date \| None = None` |
| 109 | `time_start: datetime.time = ""` | `time_start: datetime.time \| None = None` |
| 110 | `time_end: datetime.time = ""` | `time_end: datetime.time \| None = None` |
| 111-115 | `sde_type=""`, `title=TITLE_NULL`, `place=""`, `detail=""`, `debug=False` | それぞれ `: str` / `: str` / `: str` / `: str` / `: bool` を付けた |
| 132-135 | `self.sde_id = sde_id` / `self.date = date` + `if self.date is None:` の 2 行 | `self.sde_id = sde_id if sde_id else SchedDataEnt.new_id()` と `self.date = date if date is not None else datetime.date.today()`（下記 2. 参照） |
| （旧 147-148） | `if not self.sde_id: self.sde_id = SchedDataEnt.new_id()` | 削除（133 行に統合） |
| 221 | `type_is_todo(cls, sde_type: str)` | `sde_type: str \| None` |
| 296 | `set_date(self, d: datetime.date = None)` | `d: datetime.date \| None = None` |
| 344-348 | `__init__(self, date: datetime.date = None, topdir=DEF_TOP_DIR, debug=False)` | `date: datetime.date \| None = None`, `topdir: str`, `debug: bool` |
| 381-382 | `date2path(self, date: datetime.date = None, ...)` | `date: datetime.date \| None = None` |
| 469, 476 | `time_start2 = ""` / `time_end2 = ""` | `= None` |
| 540 | `del_sde(self, sde_id: str = None)` | `sde_id: str \| None = None` |
| 557 | `get_sde(self, sde_id: str = None) -> SchedDataEnt` | `sde_id: str \| None = None) -> SchedDataEnt \| None` |
| 602 | `debug=False` | `debug: bool = False` |
| 619-621 | `_sdf_cache: OrderedDict[datetime.date, SchedDataFile]` | `OrderedDict[datetime.date \| None, SchedDataFile]`（ToDo は `date=None` をキーにしているため。コメントを 1 行足した） |
| 647 | `get_sdf(self, date: datetime.date = None)` | `date: datetime.date \| None = None` |
| 689-691 | `get_sde(self, date: datetime.date = None, sde_id: str = "") -> SchedDataEnt` | `date: ... \| None`、戻り値 `SchedDataEnt \| None` |
| 715 | `add_sde(self, date: datetime.date = None, sde: SchedDataEnt = None)` | `add_sde(self, date: datetime.date \| None, sde: SchedDataEnt)`（既定値を外した。下記 6. 参照） |
| 730-732 | `del_sde(self, date: datetime.date = None, sde_id: str = "")` | `date: datetime.date \| None = None` |

docstring の `date: datetime.date` なども、実体に合わせて
`date: datetime.date | None` に直した（`get_sde()` には
「見つからない場合は None」を足した）。

### `src/ytsched/main_handler.py`

| 行 | 変更前 | 変更後 |
| --- | --- | --- |
| 147-151 | `todo_flag = sde.is_todo()` / `if todo_flag: modified_date = sde.date` | `todo_flag = False` にしてから `if sde is not None:` の中で同じことをする（`get_sde()` が `SchedDataEnt \| None` になったため） |
| 207-220 | `todo_days_value` を `str \| None` → `int` と使い回していた | 文字列用に `todo_days_str` を分け、`int(todo_days_str)` の結果だけを `todo_days_value` に入れる。既定値も `str(self.DEF_TODO_DAYS)` にした |
| 458-460 | `def exec_update(self, cmd: str) -> (datetime.date, str):` | `-> tuple[datetime.date \| None, str \| None]:`（下記 5. 参照） |
| 554 | `sde_id = self.get_argument("sde_id")` | `sde_id: str \| None = self.get_argument("sde_id")`（後で `cmd == "add"` のとき `None` を入れるため） |

319 行の `datetime.timedelta(todo_days_value)` と 404 行の
`todo_days_value >= 0` は、`todo_days_value` が `int` になったので
そのままで通るようになった（触っていない）。

### `src/ytsched/edit_handler.py`

77-81 行（5 行）を 2 行にした。下記 4. 参照。

### `tests/test_ytsched.py`

| 行 | 変更前 | 変更後 |
| --- | --- | --- |
| 9 | — | `from typing import Any` を追加 |
| 28 | `param = {` | `param: dict[str, Any] = {`（`mk_sde()` の `SchedDataEnt(**param)` で `dict[str, object]` と推論され、引数の型が合わなくなるため） |
| 696-698 | `assert sd.get_sde(DATE1, "id-1").title == "タイトル"` | 一旦 `sde` に受けて `assert sde is not None` を挟んでから `sde.title` を見る |

**テストの件数は 161 のまま**（アサーションを 1 つ足しただけで、
テスト関数は増減していない）。

## 2. `time_start` / `time_end` の `None` 化で触った箇所

**真偽判定（`if self.time_start:` など）は 1 か所も変えていない。**
`''` も `None` も falsy なので、そのままで意図どおり動く。
テンプレート（`sde.html` / `edit.html`）も真偽判定だけなので変更なし。
`mk_dataline()` の出力は変わらない（実際にデータファイルを見て確認した。
下記「自分で確かめたこと」）。

真偽判定以外で触ったのは、**`SchedDataEnt.__init__` の 132-135 行**だけ。
理由は型チェックの都合で、次の 2 つ:

1. `self.sde_id` — `sde_id` に `str | None` を付けると、
   「`self.sde_id = sde_id`（`str | None`）」と
   「末尾の `if not self.sde_id: self.sde_id = new_id()`（`str`）」から
   属性の型が `str | None` と推論され、`mk_dataline()` の
   `'\t'.join([self.sde_id, ...])` が mypy / basedpyright の両方で
   エラーになる（basedpyright が TODO-004 時点で 189/191 行に出していた
   `list[Unknown | str | None]` は、まさにこれ）。
   1 行にまとめて `str` に確定させた。
2. `self.date` — 同じく、`date: datetime.date | None` にすると
   `self.date` が `date | None` と推論され、`__str__` などの
   `self.date.strftime()` が全部エラーになる。
   元の `self.date = date` / `if self.date is None: self.date = today()` は
   隣り合う 2 文だったので、そのまま 1 文にまとめた。

**挙動の違い**: 1. で `new_id()` の呼び出し位置が `__init__` の末尾から
先頭寄りに移った。`new_id()` は `uuid.uuid4()` を作って debug ログを
出すだけなので、**結果は変わらない**（debug ログの出る順番だけが変わる）。
`sde_id=""` を渡している `edit_handler.py:101` も従来どおり新 ID になる。
2. は `if date is not None` と書いたので、元の `is None` 判定と完全に同じ。

## 3. `SchedDataFile.load()` の `time_start2` / `time_end2`

`= ""` を `= None` にしただけ。
`if` 側で `datetime.time`、`else` 側で `None` を代入する形になるが、
**mypy も basedpyright も明示の型宣言なしで通った**（一度
`time_start2: datetime.time | None` の宣言行を足す版も作って比べたが、
無くても両方 0 件だったので、差分を小さくするため入れていない）。

## 4. `edit_handler.py:77` の直し方

変更前:

```python
todo_flag = self.get_argument("todo_flag", False)
if todo_flag == "true":
    todo_flag = True
else:
    todo_flag = False
```

変更後:

```python
todo_flag_str = self.get_argument("todo_flag", "")
todo_flag = todo_flag_str == "true"
```

**挙動が変わらないと判断した根拠**（tornado 6.5 の実装を
`inspect.getsource(tornado.web.RequestHandler._get_argument)` で確認した）:

```python
args = self._get_arguments(name, source, strip=strip)
if not args:
    if isinstance(default, _ArgDefaultMarker):
        raise MissingArgumentError(name)
    return default
return args[-1]
```

- 引数が無いとき、`default` が「省略時の目印」でなければ**そのまま返す**。
  `False` も `""` も目印ではないので、返るのは `False` / `""` の違いだけ
- 直後の比較は `== "true"` なので、`False == "true"` も `"" == "true"` も
  **どちらも `False`**。つまり「引数が無ければ `todo_flag = False`」で同じ
- 引数があるときは `args[-1]`（`str`）が返るので、`default` は無関係

`todo_flag` に入る値も、変更前後とも **`True` / `False` の bool** で同じ。
（変更前が URL ルーティング由来の引数 `todo_flag` を無条件に上書きして
しまう点は、変更後もそのまま。挙動を変えないため触っていない。）

## 5. `exec_update()` の戻り値型についての判断

依頼では `-> tuple[datetime.date, str]` とあったが、
**`-> tuple[datetime.date | None, str | None]` にした。**

理由: この関数は実際に `None` を返す。

- `date` は 482 行で `None` に初期化され、`date` 引数が無ければ `None` の
  まま返る。さらに 585-586 行で「ToDo なら `date = None`」としている
- `modified_sde_id` は 562 行で `None` に初期化され、`cmd == "del"` では
  `None` のまま返る

`tuple[datetime.date, str]` と書くと、`check_untyped_defs = true` の下で
mypy が `return date, modified_sde_id` を**新しいエラーとして検出する**
（型を直したのに別のエラーが増える）。呼び出し側（135 行）は
`self._sd.get_sdf(modified_date)` と `sdf.get_sde(modified_sde_id)` に
渡すだけで、どちらも今回 `| None` を受け付けるようにしたので、
`| None` 付きの戻り値型でそのまま通る。docstring も実体に合わせた。

## 6. `SchedData.add_sde()` の既定値を外した判断

`add_sde(self, date: datetime.date = None, sde: SchedDataEnt = None)` の
`sde` は、`None` のまま呼ばれると
`sdf.add_sde(None)` → `sorted(key=get_sortkey)` で AttributeError になる。
つまり `= None` は最初から意味の無い既定値だった。

`sde: SchedDataEnt | None = None` にすると `sdf.add_sde(sde)` が
型エラーになるので、次のどれかが要る:

- (a) `sde is None` を弾く分岐を足す → **無かった挙動を足すことになる**
- (b) `assert` / `cast` を入れる → 型を誤魔化すだけ
- (c) **既定値を外して `sde: SchedDataEnt` にする**（`sde` の前にある
  `date` の既定値も外れる）

**(c) を選んだ。** 実行時の振る舞いを一切足さずに型が正しくなるため。
呼び出しは `main_handler.py`（2 か所）と
`tests/test_ytsched.py`（3 か所）だけで、**すべて 2 引数を位置引数で
渡している**ので、この変更で壊れるものは無い（`grep` で確認済み。
pytest も 161 passed のまま）。

これは依頼の箇条書きに無い判断なので、main の確認をお願いしたい。

## 7. mypy / basedpyright の結果

### mypy（`uv run mypy src tests`）

| | 件数 |
| --- | --- |
| 変更前 | **35 件**（5 ファイル） |
| 変更後 | **2 件**（2 ファイル） |

残った 2 件は、依頼で「直さない」とされた TODO-007 の範囲のもの:

```
src/ytsched/ytsched.py:357: error: Name "__class__" is not defined  [name-defined]
src/ytsched/__main__.py:22: error: Name "__class__" is not defined  [name-defined]
```

**それ以外は全部消えた。**

### basedpyright（`uv run basedpyright src tests`）

| | 件数 |
| --- | --- |
| 変更前 | **28 errors, 2 warnings** |
| 変更後 | **0 errors, 0 warnings, 0 notes** |

依頼で「消えるはず」とされていたもの（`ytsched.py:189, 191` の
`'\t'.join()`、`309, 402` の `reportUnreachable`、`edit_handler.py:77`、
`tests/test_ytsched.py` の 8 件）も**すべて消えた**。
basedpyright は `__class__` を理解するので、mypy に残る 2 件は出ない。

### ruff

`uv run ruff check --extend-select I src tests`
**97 件 → 87 件**。減った 10 件は `RUF013`（implicit-optional）ちょうど
10 件で、これが今回の範囲。残る 87 件（`UP031` 35、`DTZ011` 13、
`FLY002` 13、`D419` 10、`RUF012` 5、`EXE001` 4、ほか 7）は
**TODO-015 / TODO-008 の範囲**なので触っていない。
新しく増えた指摘は無い。

## 自分で確かめたこと

| 確認 | 結果 |
| --- | --- |
| `uv run pytest tests` | **161 passed**（変更前と同じ件数） |
| `uv run mypy src tests` | 2 件（上記の `__class__` のみ） |
| `uv run basedpyright src tests` | 0 errors, 0 warnings |
| `uv run ruff format --line-length 78 src tests` | 適用済み。最終状態で `13 files left unchanged` |
| 78 文字超の行 | `awk 'length > 78' src/ytsched/*.py tests/*.py` で **0 件** |
| `uv run ruff check --extend-select I src tests` | 87 件（変更前 97 件、差は `RUF013` 10 件だけ） |
| webapp の起動 | `--datadir` に一時ディレクトリを指定して `--port 10099` で起動。`/ytsched/`、`/ytsched/edit`、`/ytsched/edit?todo_flag=true` がいずれも **200** |
| データ形式（重要） | 同じ一時 datadir に対して `cmd=add` を 3 回（時刻あり／時刻なし／ToDo）POST し、書かれたファイルを `cat -A` で確認。**7 項目のタブ区切り、時刻なしは `:-:`、時刻ありは `09:05-10:30` で従来どおり**。終了時刻だけ空の場合も `05:45-:` と出る |
| 更新・削除の経路 | `cmd=update` / `cmd=del` / ToDo の `cmd=fix`（完了 → 今日の日付へ移動 + `〆` 付き detail）を POST して、いずれも 200 かつファイルの中身が期待どおりであることを確認 |

確認に使った webapp は停止済み（`~/ytsched/data` は触っていない）。

## 単独で決めた判断（まとめ）

1. **`exec_update()` の戻り値型を `tuple[datetime.date \| None, str \| None]`
   にした**（依頼は `tuple[datetime.date, str]`）。上記 5. の理由
2. **`SchedData.add_sde()` の `date` / `sde` から既定値を外した。**
   上記 6. の理由。**main の確認が要ると思う点**
3. **`SchedDataEnt.__init__` の `sde_id` / `date` の代入を 1 文にまとめた。**
   上記 2. の理由。`new_id()` の呼び出し位置が変わるが結果は同じ
4. **`_sdf_cache` のキーの型を `datetime.date | None` にした。**
   ToDo を `date=None` のキーで扱っているので、TODO-004 で入れた
   `datetime.date` は実体と合っていなかった
5. **`type_is_todo()` の引数を `str | None` にした。**
   本体が `if sde_type:` で falsy を弾いており、
   `tests/test_ytsched.py:251` が意図して `None` を渡している。
   テストを直すのではなく、本体の型を実体に合わせた
6. **`tests/test_ytsched.py` の `param` に `dict[str, Any]` を付けた。**
   `SchedDataEnt.__init__` の引数に型を付けたことで
   `SchedDataEnt(**param)` が合わなくなるため。テストの意図は変えていない
7. **`load()` の `time_start2` / `time_end2` に型宣言を足さなかった。**
   無くても mypy / basedpyright とも通ることを実際に比べて確認した

## 直さずに残したもの

- `ytsched.py:357` と `__main__.py:22` の `Name "__class__" is not defined`
  — 依頼どおり **TODO-007**（loguru 移行）の範囲。mypy に 2 件残る
- `ruff` の 87 件（`UP031` / `DTZ011` / `FLY002` / `D419` / `RUF012` /
  `SIM102` ほか）— **TODO-015** の範囲
- `EXE001`（shebang）4 件 — **TODO-008** の範囲
- `EditHandler.get(self, date=None, sde_id=None, todo_flag=False)` の
  引数に型注釈が無い（TODO-004 の報告にも挙がっていない）。
  mypy / basedpyright とも指摘しないので、範囲を広げずに残した。
  `todo_flag` 引数が本文で無条件に上書きされている件も、**挙動を変えない**
  ため触っていない（気になるなら別項目にするのがよいと思う）
- `handler.py` の `get_conf()` / `set_conf()` / `load_conf()` などにも
  型注釈が無いが、型チェッカーが通っているので触っていない

## うまくいかなかったところ

特に無し。`pgrep` でプロセスを止める際に自分のシェルを巻き込んで
1 回エラー終了したが、`ps` で残っていないことと、ポート 10099 に
つながらないことを確認済み。
