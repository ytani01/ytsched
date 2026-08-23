# TODO-027 reviewer の報告

`git diff`（`src/ytsched/main_handler.py`、`tests/test_main_handler.py`、
`tests/test_web.py`）を読んだ。コードは直していない。

先に、依頼書で聞かれた点のうち**問題が無かった**ものを書いておく。

- **`get_date()` の優先順位は変わっていない。** `year`+`month`+`day` →
  `modified_date` → `date` → `cur_day` → 今日。不正な値を「無かった」ことに
  したときの繰り上がりも、`date` が `None` になって `cur_day` へ落ちる形で
  意図どおり
- **`ymd2date()` は 3 つ揃ったときだけ効く。** `if year and month and day`
  の条件は元のまま。1 つでも欠ければ呼ばれない
- **`set_conf()` の抜け道は無い。** `set_conf()` の呼び出しは
  `get_conf_arg()` の 1 か所だけで、`converted is not None` の中にある
  （ただし後述の指摘 2 を除く）
- **`converted is not None` で判定しているのは正しい。** truthy で見ていたら
  `search_n=0` や空の `search_str` が落ちていた
- **警告の形は既存に揃っている。** `f"... .. ignored"` は `handler.py`・
  `ytsched.py`・`migrate.py` と同じ書き方。`__log = getLogger(__qualname__)`
  も MainHandler に 1 つのままで、増やしていない

---

## 確信度の高い指摘

### 1. `ymd2date()` が `OverflowError` を拾えず、`year` が大きいと 500 のまま

`src/ytsched/main_handler.py:511-517`

```python
try:
    return datetime.date(int(year), int(month), int(day))
except ValueError as ex:
```

`datetime.date()` は年が C の `int` に収まらないと **`OverflowError`** を
投げる（`ValueError` のサブクラスではない）ので、この `except` を素通りする。

実測（テスト用の一時 datadir で `AsyncHTTPTestCase` から）:

| 入力 | 結果 |
|---|---|
| `?year=99999999999&month=1&day=1` | **500** |
| `?year=0&month=1&day=1` | 200（`ValueError` なので拾える） |
| `?year=10000&month=1&day=1` | 200（同上） |

`OverflowError: signed integer is greater than maximum`。

**なぜ問題か。** `ymd2date()` の docstring は「`month=13`/`day=32` のような
**範囲外**も `None` を返す」と書いているが、範囲外の一部で成り立っていない。
`TODO.md` の TODO-027 も「`month=13`、`day=32` のような範囲外も含む」と
明示しているので、**項目の範囲内の取りこぼし**。

**どうなると困るか。** URL を手で組み立てた（あるいはリンクが壊れた）ときに
500 が返る。`year`/`month`/`day` は `Conf.cgi` に保存されないので居座りは
しないが、「不正な入力で 500 にしない」という項目の目的は達していない。

なお `int(year)` 側は 4300 桁を超えると `ValueError` になって拾えるので、
**桁数がその手前のときだけ**すり抜ける。境界が分かりにくい。

### 2. `todo_days` に巨大な数字を渡すと `Conf.cgi` に保存され、以後ずっと 500

`src/ytsched/main_handler.py:143-149`（保存）、`615`（落ちるところ）

`int("99999999999")` は成功するので `get_conf_arg()` は「正しい値」と見なし、
`set_conf()` で `Conf.cgi` に書く。そのあと `load_todo()` の

```python
if sde.date > today + datetime.timedelta(todo_days_value):
```

が `OverflowError: Python int too large to convert to C int` で落ちる。

実測（`ToDo.jsonl` に 1 件書いた状態）:

| 手順 | 結果 |
|---|---|
| `?todo_days=99999999999` | **500** |
| そのときの `Conf.cgi` | `ToDo_Days\t99999999999\n` が**書かれている** |
| そのあとの素の `GET /ytsched/` | **500** |

**なぜ問題か。** これは TODO-027 が直そうとしている失敗そのもの
（「一度踏むと `Conf.cgi` に残って、トップページも開けなくなる」）が、
別の入力で残っているということ。`Conf.cgi` を手で消すまで復旧できない。

**どうなると困るか。** ToDo が 1 件も無いと `for sde in todo_sdf.sde` に
入らないので落ちない。**ToDo がある実データでだけ起きる**ので、今の
テスト（`TestInvalidArgs` は ToDo を置いていない）では絶対に出ない。

字面の上では「数字にならない値」ではないので TODO-027 の範囲外とも読める。
**この項目で直すか、TODO を立て直すかは main の判断。**

### 3. `search_n` の `empty_is_given=True` が外から観測できなくなり、
ゴールデンマスターテストが 1 つ効かなくなった

`tests/test_main_handler.py:47-55`（`TestConfArgs` の docstring）、
`110-126`（書き直した 2 件）

`int("")` は必ず失敗するので、`empty_is_given=True` で空文字が分岐に入っても、
そのまま `Conf.cgi` → 既定値へ落ちる。これは `empty_is_given=False`
（truthy 分岐で最初から入らない）と**結果が完全に一致する**。つまり
**`convert=int` の 2 か所では `empty_is_given` の `True`/`False` に差が無い**。

その結果:

- `TestConfArgs` の docstring 「`search_str` と `search_n` は `is not None`
  で、`todo_days` と `filter_str` は truthy で分岐する。**空文字を渡した
  ときだけ差が出る**」は、`search_n` について成り立たなくなった。docstring は
  今回直されていない
- 書き直した `test_empty_search_n_is_not_saved` は「200 で `Conf.cgi` が
  作られない」しか見ていない。**`search_n` を truthy 分岐に変えても通る**

**どうなると困るか。** TODO-028 に「4 か所の食い違い」を触る項目がある
（`filter_str` を空で解除できるようにする）。そのとき `search_n` の分岐を
一緒に揃えても、**落ちるテストが無いので気づけない**。TODO-021 で
「いまこう動く」を押さえるために足したテストなので、押さえが 1 つ緩んだ
ことは記録しておくべき。

---

## 確信度の低いもの・この項目の範囲外かもしれないもの

### 4. 極端だが「正しい」日付では、まだ 500 になる

変換には成功するので今回の仕組みでは拾えない。実測:

| 入力 | 結果 |
|---|---|
| `?date=9999-12-31` | 500 |
| `?date=0001-01-01` | 500 |
| `?year=9999&month=12&day=31` | 500 |

`load_sched()` の `date_from = date - datetime.timedelta(self._days)` /
`date_to = date + ...` が `OverflowError`。指摘 2 と同じ根（**変換に成功した
あとの値の範囲を誰も見ていない**）。

項目の字面（数字・日付にならない値）の外だが、タイトル「不正な入力で 500 に
なるのをやめる」からは外れている。指摘 2 とまとめて扱うのが素直だと思う。

### 5. `get_date()` の判定が truthy と `is not None` で揃っていない

`main_handler.py:459`（`if parsed:`）、`481`（`if parsed:`）に対して
`get_conf_arg()` は `if converted is not None:`。`datetime.date` は常に
truthy なので**今は正しい**。挙動の誤りではないが、`convert_value()` が
`T | None` を返す設計である以上、`is not None` で揃っているほうが
「None かどうかを見ている」と読める。

### 6. `convert=str` は検証になっていない

`str()` は失敗しないので、`search_str`/`filter_str` では `convert` が常に
恒等関数。型引数 `T` を決めるためだけに必須にした形で、動作は正しい。
ただし呼び出し 4 か所が同じ見た目になるので、「4 つとも検証を通している」と
読めてしまう。docstring にその旨があると誤解が減る。

### 7. `ymd2date()` が `convert_value()` を使っていない

`try`/`except ValueError` と警告の組み立てが 2 か所に分かれている。3 つ揃わ
ないと日付にできないので `convert_value()` に載らないのは分かるが、
**指摘 1 のように拾う例外を増やすとき、直す場所が 2 か所になる**。

### 8. 足したテストについて

`TestInvalidArgs`（18 件）は実装に合わせただけではなく、挙動を固定するもの
になっている。特に `test_invalid_search_n_keeps_saved_search_n` は、
implementer が「依頼書の文面と違う」と申告した判断をそのままテストにして
いるので、方針を変えるときに落ちる。良い形。

気づいた抜け:

- `search_n` には「保存済みの値が消えない」テストがあるのに、`todo_days` に
  は無い（同じ落ち方をするので、片方だけなのは対称でない）
- **警告ログが出ることを見ているテストが無い。** 「500 にしない」だけなら
  黙って捨てても通る。TODO-027 は「ログに警告を出す」も箇条書きに入って
  いるので、1 件くらいは `caplog` で押さえてよいと思う
- ToDo がある状態での `todo_days` のテストが無い（指摘 2 が見つからなかった
  理由）

### 9. 型の付け方（PEP 695）について

`def convert_value[T](...)` / `def get_conf_arg[T](...)` は、このリポジトリ
**初めての**ジェネリック（`TypeVar` も含めて他に用例が無い）。3.14 なので
問題は無く、`TypeVar` を別に宣言するより短い。浮いているとまでは言えない。
指摘ではなく、依頼書の 6 番への回答として書いておく。

---

## main の判断が要ると思うところ

1. **指摘 1**（`year` が大きいと 500）は、項目の範囲内の取りこぼし。
   この項目で直すのが素直
2. **指摘 2・4**（変換に成功した「範囲外」の値で 500、うち `todo_days` は
   `Conf.cgi` に居座る）は、字面では範囲外。**この項目に足すか、
   TODO-032 として立てるか**
3. **指摘 3** の `TestConfArgs` の docstring と、押さえが緩んだ件。
   TODO-028 に申し送るだけでもよい
4. implementer が申告した「引数が不正なら `Conf.cgi` の値へ落とす」は、
   `search_str`/`filter_str`/`search_n`/`todo_days` の 4 か所とも破綻して
   いないことを確かめた（`convert=str` の 2 か所は挙動が完全に不変、
   `convert=int` の 2 か所は指摘 3 のとおり `empty_is_given` の差が消える
   だけ）。**方針として問題は無いと思う**
