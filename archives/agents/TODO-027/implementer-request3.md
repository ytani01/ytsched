# TODO-027 implementer への依頼（3 回目）

2 回目の実装に reviewer が指摘を出した。報告は
`archives/agents/TODO-027/reviewer-report2.md`。**先に読むこと。**
1 回目の指摘 1・2・4 は直っていると確認された。残りを片付ける。

利用者と相談して、**指摘 1・2・3 の 3 件ともこの項目で直す**と決めた。
`/edit` まで含めて、**画面全体で「不正な入力で 500 にならない」形にする**。

## 直すもの

### A. 指摘 1 — `str2ymd_date()` が `month`/`day` の範囲を見ていない

年だけ `datetime.MINYEAR..MAXYEAR` を見ていて、月・日は `int()` を
通しただけで `datetime.date()` に渡している。C の `int` に収まらない
月・日は `OverflowError`（`ValueError` のサブクラスではない）になる。

- `?year=2021&month=99999999999&day=1` → **500**
- `?year=2021&month=1&day=99999999999` → **500**
- `?year=2021&month=1&day=-99999999999` → **500**

年と同じ形で、**`datetime.date()` を呼ぶ前に**弾く。
`ymd2date()` の docstring の「範囲外も `None` を返す」が、今度こそ
全部で成り立つようにする。

### B. 指摘 2 — 更新経路の `date`（`get_date_arg()`）

`cmd=add`/`fix`/`update`/`del` の `date`・`orig_date` は、形式も範囲も
見ていない。**日付として読めない値も 500 になる**（`Conf.cgi` の話とは
別に、TODO-027 が挙げた `date` の直し残し）。

- `cmd=add&date=abc&title=test&sde_id=` → 500
- `cmd=add&date=9999-12-31&title=test&sde_id=` → 500

reviewer は「`get_date_arg()` を `convert_value(..., self.str2date)` に
載せるだけで形式と範囲の両方が片付く」と書いている。

**ただし、落ちたあとどうするかは考えること。** 表示経路は「指定が
無かったのと同じ」でよかったが、こちらは**データを書き込む**経路。

- `date` が読めないときは、`SchedDataEnt` 側で今日に補正される
  （TODO-016 で `date` が空の POST をそう決めた）ので、`None` にして
  その経路へ乗せるのが素直
- `orig_date` が読めないときは、`cmd_del()` の行き先が変わる。
  **消し間違いが起きない形**にすること（`None` は ToDo のファイルを
  指すので、そのまま `None` にしてよいかは考えること）
- 迷ったら、**判断の理由を報告に書く**

### C. 指摘 3 — `EditHandler` の `date`

`src/ytsched/edit_handler.py` の
`date = datetime.date.fromisoformat(date_str)` が素通し。
`/ytsched/edit?date=abc` は 500。

- ここは `MainHandler` ではないので、`convert_value()` / `str2date()` を
  どう共有するかを考えること。**`HandlerBase` へ上げるのが素直だと
  思うが、置き場所は任せる**（`date_range()` が `self._days` を使うので、
  `HandlerBase` にも `self._days` があることを確かめてから決める）
- 読めない値は「指定が無かったのと同じ」＝今日にする

## ついでに直すもの（指摘 4）

`tests/test_main_handler.py` の `TestConfArgs` の docstring に
「`search_n`/`todo_days` は `convert=int` で」とあるが、`todo_days` の
`convert` は `str2todo_days()`。**結論は変わらないが、TODO-028 で読ませる
ための docstring なので辿れる形に直す。**

## 直さないもの

- 指摘 5（上端の余裕がテストで押さえられていない）は直さなくてよい。
  reviewer も「直す必要は無い」と書いている
- 指摘 6（`--days` を極端に大きくすると `date_range()` 自体が落ちる）は
  **この項目でやらない**。CLI の値なので別の話
- 指摘 7（`Conf.cgi` が不正な間、毎回警告が出る）はそのまま

## テスト

- A・B・C それぞれについて、**500 にならないこと**を確かめるテストを
  足す。B は**書き込んだ結果がどうなったか**（どの日のファイルに入り、
  消し間違いが起きていないか）まで見ること
- 既存の 361 件が通ることを確かめる

## 決まりごと

- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は走らせない**
- アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する
- 報告は `archives/agents/TODO-027/implementer-report3.md` に書く。
  返事は 5 行以内
