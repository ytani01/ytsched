# TODO-027 reviewer の報告（2 回目）

`git diff`（`src/ytsched/main_handler.py`、`tests/test_main_handler.py`、
`tests/test_web.py`）を読み、確かめたいところは**リポジトリの外
（scratchpad）に一時的なテストを書いて実測**した。コードは直していない。
リポジトリには何も足していない（`git status` で確認済み）。

## 直っているもの

依頼書の 1・2・6 に対する答えを兼ねる。**1 回目の指摘 1・2・4 は直っている。**

- **指摘 1（`year` の `OverflowError`）は、`year` については直っている。**
  `str2ymd_date()` が `datetime.MINYEAR..MAXYEAR` を `datetime.date()` を
  呼ぶ前に見るので、`?year=99999999999&month=1&day=1` は 200。
  **ただし `month`/`day` は同じ穴が残っている**（後述の指摘 1）
- **指摘 2（`todo_days` が `Conf.cgi` に居座って以後ずっと 500）は
  直っている。** `str2todo_days()` が範囲外を `ValueError` にするので
  保存されず、既に入っている値も読むときに落とされる。ToDo を 1 件
  置いた状態のテストも足されている
- **指摘 4（極端だが正しい日付で 500）は直っている。**
  `date`/`cur_day`/`year+month+day` の 3 経路とも `check_date()` を通る
- **範囲の決め方に off-by-one は無い。** `load_sched()` が実際に触る
  いちばん先の日付は `date_to + DELTA_DAY1` ＝ `date + self._days`、
  いちばん手前は `date_from = date - max(self._days,
  SEARCH_MODE_MAX_DAYS)`（検索モード）。`margin = max(self._days,
  SEARCH_MODE_MAX_DAYS)` はどちらも覆う。**下端は 1 日の余裕も無い
  ぴったりの幅**で、テスト
  `test_the_oldest_usable_date_works_in_search_mode` が実際にそこを
  押さえている（範囲を 1 日でも広げると 500 になって落ちる）
- **`ymd2date()` の `/` 連結は、思わぬ入力で変な通り方をしない。**
  実測で `?year=1/2&month=3&day=4` は 200（`split("/")` が 4 要素に
  なり unpack が `ValueError`）。`year=-5` のような負値も分けられる
- **警告メッセージは読んで分かる形。** `year/month/day='2021/13/1':
  month must be in 1..12, not 13 .. ignored` は、`datetime` の
  言い回しに揃っていて、どの引数の組かも分かる。1 回目より短い
- **指摘 3・5・6・7・8 は依頼書のとおり片付いている。**
  `TestConfArgs` の docstring は「外から差が見えるのは
  `search_str`/`filter_str` の 2 か所だけ」「ここのテストは落ちない
  （TODO-028）」と書かれていて、TODO-028 で読んで役に立つ形になって
  いる（**言い回しに 1 か所だけ不正確なところがある。指摘 4**）
- **`search_n` に範囲を付けなかった判断は妥当。** 実測でも
  `?search_n=99999999999&search_str=会議` は 200 で、探す幅は
  `SEARCH_MODE_MAX_DAYS` で頭打ち
- **`todo_days` を `-1..36500` にした判断も妥当。** 申告された副作用
  （`todo_days=-5` が off ではなく既定値へ落ちる）以外に変わるものは
  見当たらない。`TODO_DAYS` の値（-1/0/1/3/7/14/30/365/36500）は
  すべて範囲内で、`Conf.cgi` に入りうる過去の値も、
  `-1..36500` の外は `load_todo()` を壊す値だけ

---

## 確信度の高い指摘

### 1. `month`/`day` の `OverflowError` が残っている（指摘 1 の直し漏れ）

`src/ytsched/main_handler.py:355-373`（`str2ymd_date()`）

年だけを `datetime.MINYEAR..MAXYEAR` で弾いていて、`month`/`day` は
`int()` を通しただけで `datetime.date()` へ渡している。
`datetime.date()` は月・日が C の `int` に収まらないときも
**`OverflowError`**（`ValueError` のサブクラスではない）を投げる。

```python
>>> datetime.date(2021, 100000000000, 1)
OverflowError: signed integer is greater than maximum
>>> datetime.date(2021, 1, -100000000000)
OverflowError: signed integer is less than minimum
```

実測（`WebTestBase` から。いずれも **500**）:

| 入力 | 結果 |
|---|---|
| `?year=2021&month=99999999999&day=1` | **500** |
| `?year=2021&month=1&day=99999999999` | **500** |
| `?year=2021&month=1&day=-99999999999` | **500** |

トレースバックは `str2ymd_date()` の
`datetime.date(year, int(month_str), int(day_str))`（`main_handler.py:372`）
で、`convert_value()` の `except ValueError` を素通りする。

**なぜ問題か。** 1 回目の指摘 1 とまったく同じ失敗で、対象も同じ
`year`/`month`/`day`（TODO-027 の 5 か所のひとつ）。**項目の範囲内の
取りこぼし**であり、`ymd2date()` の docstring の「`month=13`/`day=32` の
ような範囲外も `None` を返す」も、また一部で成り立っていない。

**どうなると困るか。** 手で URL を組んだとき、リンクが壊れたときに
500。`year`/`month`/`day` は `Conf.cgi` に残らないので居座りはしない。

### 2. `cmd=add`/`fix`/`update`/`del` の `date` は、形式も範囲も見ていない

`src/ytsched/main_handler.py:1012-1028`（`get_date_arg()`）、
`939`（`exec_update()` から呼ぶところ）

実装者は「POST 側の `modified_date` は範囲を見ていない」と申告して
いるが、**壊れるのは範囲外の日付だけではない。日付として読めない値も
今までどおり 500 になる。**

| 入力 | 結果 | 落ちるところ |
|---|---|---|
| `cmd=add&date=abc&title=test&sde_id=` | **500** | `get_date_arg()` の `fromisoformat`（`ValueError`） |
| `cmd=add&date=9999-12-31&title=test&sde_id=` | **500** | `load_sched()`（`OverflowError`） |

`cmd` は `get_argument()` で取るので **POST の本文だけでなく
クエリ文字列でも効く**（`GET /ytsched/?cmd=add&date=abc` でも同じ）。

**なぜ問題か。** `date` は TODO-027 が挙げた 5 か所のひとつで、
GET の表示経路（`get_date()`）だけが直り、更新経路は素通しのまま。
「`date` は直した」と読める状態で片方だけ残るのは、後から見て
分かりにくい。

**どうなると困るか。** 編集フォームは `<input type="date">` なので
普通の操作では起きない。手で組んだ URL、古いブックマーク、
`date` を持ったリンクが壊れたときに 500。

**判断が要る。** 「TODO-027 の 5 か所」の `date` に更新経路を含めるか、
別項目（TODO-032 の改良案か新項目）にするか。**含めるなら、
`get_date_arg()` を `convert_value(..., self.str2date)` に載せるだけで
形式と範囲の両方が片付く**（`orig_date` も同じ経路）。

### 3. `/ytsched/edit?date=abc` は 500 のまま

`src/ytsched/edit_handler.py:61`

```python
date = datetime.date.fromisoformat(date_str)
```

実測で **500**。TODO-027 の 5 か所は `MainHandler` の話なので**項目の
範囲外**だが、症状はまったく同じ（不正な日付で 500）で、`main.html`
から `edit` へのリンクは `date` を持って飛ぶ。指摘 2 と一緒に扱うのが
素直だと思う。**この項目に入れるかは main の判断。**

---

## 確信度の低いもの・細かいもの

### 4. `TestConfArgs` の docstring の「`convert=int`」が 1 か所だけ不正確

`tests/test_main_handler.py:56-60`

「``search_n``/``todo_days`` は ``convert=int`` で」とあるが、
`todo_days` の `convert` は `str2todo_days()`（中で `int()` を呼ぶので
**結論は変わらない**）。TODO-028 で読ませるために書いた docstring
なので、`todo_days` は `str2todo_days()` で、その中の `int('')` が
失敗する、と書いてあるほうが辿りやすい。

### 5. 境界のテストは、下端は押さえているが上端は「狭くした」方向しか捕まえない

`tests/test_web.py`
（`test_the_newest_usable_date_still_works` /
`test_the_oldest_usable_date_works_in_search_mode`）

- **下端**は幅ぴったりなので、`margin` を 1 日でも広げると
  `date_from` が `date.min` を割って 500 になり、テストが落ちる。
  範囲の根拠を押さえている
- **上端**は、実際に必要な余裕が `self._days`（既定 45 日）しかない
  のに `margin`（1825 日）を引いている。つまり上端は 1780 日ぶん
  余裕がある。**`margin` の上端側を 45 まで縮めてもこのテストは
  通る**ので、「上端が広すぎる」変更は捕まえられない

余裕を持たせること自体は無害（影響するのは 9995〜9999 年だけ）で、
前後で揃えるほうが読みやすい。**直す必要は無いと思う**が、
テストが何を押さえていて何を押さえていないかは記録しておきたい。

### 6. `--days` を極端に大きくすると、`date_range()` 自体が `OverflowError`

`src/ytsched/main_handler.py:299-302`

`margin = datetime.timedelta(max(self._days, SEARCH_MODE_MAX_DAYS))` は、

- `--days 1000000000` → `timedelta()` が `OverflowError`
  （`must have magnitude <= 999999999`）
- `--days 4000000` → `date.min + margin` が `OverflowError`

になり、`date`/`cur_day`/`year+month+day` を付けたリクエストが 500。
ただし `--days` は CLI（管理者）の値で、その桁では `load_sched()` の
ループが何百万日ぶん回るので**元々使いものにならない**。
`--days` に上限を付けるなら別項目。**この項目でやることではない。**

### 7. 不正な値が `Conf.cgi` に残っている間、毎リクエスト警告が出る

1 回目と同じ（消し込みはしない）。既定値へ落ちて画面は出るので実害は
無いが、`Conf.cgi` を直すまで警告が出続けることは変わっていない。

---

## main の判断が要るところ

1. **指摘 1（`month`/`day` の `OverflowError`）は、項目の範囲内の
   取りこぼし。この項目で直すのが素直**（`str2ymd_date()` の年の
   チェックを月・日にも広げるだけで済む）
2. **指摘 2（更新経路の `date`）**を TODO-027 の `date` に含めるか、
   別項目にするか。含めるなら `get_date_arg()` を `convert_value()` に
   載せるだけ
3. **指摘 3（`EditHandler` の `date`）**は範囲外。指摘 2 と同じ扱いに
   するのが自然
4. 指摘 4（docstring の不正確な 1 語）は、TODO-028 のついででもよい
