# TODO-027 implementer への依頼（2 回目）

1 回目の実装に reviewer が指摘を出した。報告は
`archives/agents/TODO-027/reviewer-report.md`。**先に読むこと。**
利用者と相談して、**指摘 1・2・4 の 3 件ともこの項目で直す**と決めた。
「不正な入力で 500 になるのをやめる」という項目のタイトルを満たす形にする。

## 直すもの

### A. 指摘 1 — `ymd2date()` が `OverflowError` を拾えない

`?year=99999999999&month=1&day=1` が 500 のまま。`OverflowError` は
`ValueError` のサブクラスではないので `except ValueError` を素通りする。

### B. 指摘 2 — `todo_days` に巨大な数字を渡すと `Conf.cgi` に居座って 500

`int("99999999999")` は成功するので保存され、`load_todo()` の
`today + datetime.timedelta(todo_days_value)` が `OverflowError` で落ちる。
ToDo が 1 件でもあると、**以後ずっとトップページが開けない**。
これは TODO-027 が直そうとした失敗そのもの。

### C. 指摘 4 — 極端だが「正しい」日付で 500

`?date=9999-12-31` / `?date=0001-01-01` / `?year=9999&month=12&day=31` が、
`load_sched()` の `date - datetime.timedelta(self._days)` などで
`OverflowError`。

## 方針

- 根は 1 つ（**変換に成功したあとの値の範囲を誰も見ていない**）なので、
  **3 件をばらばらに継ぎ当てせず、まとめて扱える形にする**。例えば
  「変換したあとに、使える範囲かどうかも見る」形にして、範囲外なら
  変換できなかったのと同じ扱い（既定値へ落として警告 1 行、
  `Conf.cgi` へ保存しない）にする
- 落とし先と警告の出し方は 1 回目と揃える。`Conf.cgi` に既に入って
  しまっている場合も、読むときに既定値へ落とす（1 回目と同じ）
- **`OverflowError` を拾うだけで済ませない。** 「実際に落ちるところで
  例外を捕まえる」のではなく、**入り口で弾く**こと。`load_todo()` や
  `load_sched()` に `try` を足す形は採らない（落ちる場所が増えるたびに
  継ぎ当てが要る）
- 範囲の決め方は任せるが、**なぜその範囲かをコードのコメントか
  docstring に書く**こと。`datetime.date` の `MINYEAR`/`MAXYEAR` と、
  そこから `self._days` や `SEARCH_MODE_MAX_DAYS` を足し引きしても
  はみ出さないか、が判断の材料になるはず
- `ymd2date()` が `convert_value()` と別に `try`/`except` を持っている件
  （指摘 7）は、まとめられるならまとめてよい

## ついでに直すもの（reviewer の指摘 3・8）

- `tests/test_main_handler.py` の `TestConfArgs` の docstring が実態と
  合わなくなっている（`int("")` が必ず失敗するので、`convert=int` の
  2 か所では `empty_is_given` の `True`/`False` に差が無い）。**docstring を
  今の実態に書き直す。** この事実は TODO-028 で `empty_is_given` を
  揃えるときに効くので、**そう読める形で書いておく**こと
- `todo_days` にも「保存済みの値が消えない」テストを足す
  （`search_n` にはあるのに対称でない）
- **警告ログが出ることを見るテストを 1 件足す**（`caplog` などで）。
  TODO-027 は「ログに警告を出す」も箇条書きに入っているのに、今は
  黙って捨てても通る
- **ToDo がある状態での `todo_days` のテスト**を足す（B が今の
  テストで見つからなかった理由がこれ）

## 直さないもの

- 指摘 5（`if parsed:` と `if converted is not None:` の不揃い）は、
  `is not None` に揃えてよい。挙動は変わらない
- 指摘 6（`convert=str` は検証になっていない）は、docstring に
  一言足すだけでよい
- 指摘 9（PEP 695）は指摘ではないので何もしない
- `src/README.md` への追記は、この項目ではしない

## テスト

- A・B・C それぞれについて、**500 にならないこと**と、
  **`Conf.cgi` に不正な値が残らないこと**を確かめるテストを足す。
  B は **ToDo を 1 件置いた状態**で見ること
- 既存の 348 件が通ることを確かめる

## 決まりごと

- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は走らせない**
- アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する
- 報告は `archives/agents/TODO-027/implementer-report2.md` に書く。
  返事は 5 行以内
