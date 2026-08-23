# TODO-027 implementer への依頼

項目そのものは `TODO.md` の「TODO-027. 不正な入力で 500 になるのをやめる」。
背景と決めたことはそちらに全部書いてあるので、**先に読むこと**。

## やること

不正な入力（数字・日付として読めない値）で 500 にせず、既定値へ落として
警告ログを出す。対象は次の 5 か所（すべて `src/ytsched/main_handler.py`）。

1. `search_n` — `int(search_n_str)` が `ValueError` になる
2. `todo_days` — `int(todo_days_str)` が `ValueError` になる
3. `date` — `datetime.date.fromisoformat()` が `ValueError` になる
4. `cur_day` — 同上
5. `year`/`month`/`day` — `int()` と `datetime.date()` が
   `ValueError` になる（`month=13`、`day=32` のような範囲外も含む）

## 方針

- **落とす先は今の既定値**。`search_n` は `DEF_SEARCH_N`、`todo_days` は
  `DEF_TODO_DAYS`、`date`/`year,month,day` は「指定が無かったのと同じ」
  扱い（`cur_day`、それも無ければ今日）、`cur_day` は今日
- **警告は `self.__log.warning()` で 1 行**。何がどう不正だったかが
  分かる形にする。扱い方は TODO-012（不正な正規表現はその条件を無視して
  全件を出す）に揃える
- **不正な値を `Conf.cgi` へ保存しない。** いま `get_conf_arg()` が
  引数を無検査で `set_conf()` している。ここを直さないと、`search_n=abc`
  を一度踏むと `Conf.cgi` に残り、次からトップページも開けない
  （これがこの項目の主目的）
- **`Conf.cgi` に既に不正な値が入っている場合も、読むときに既定値へ
  落とす。** 保存側だけ直しても、踏んでしまった `Conf.cgi` は直らない
- 実装の形は任せるが、`get_conf_arg()` に検証を渡す（例: 変換関数を
  受け取り、失敗したら既定値を返して保存もしない）形が素直だと思う。
  4 つの取り出し方が揃っていない件（`empty_is_given`）は、この項目では
  揃えなくてよい

## テスト

- TODO-021 で足したゴールデンマスターテストが落ちる。**挙動を変えたの
  だから書き直してよい**（`tests/README.md` にそう書いてある）
- 不正な値それぞれについて、**500 にならず既定値で描画されること**を
  確かめるテストを足す。`Conf.cgi` に不正値が保存されないことも確かめる
- 既に `Conf.cgi` に不正値が入っている状態から開けることも確かめる

## 決まりごと

- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は走らせない**
- アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する
- 終わったら報告を `archives/agents/TODO-027/implementer-report.md` に
  書く。返事は「終わったか・報告のパス・判断が要る点」の 5 行以内
