# TODO-027. 不正な入力で 500 になるのをやめる

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort high、担当 = implementer ×4 + verifier ×4 + reviewer ×3

- [x] 数字・日付にならない値を既定値へ落とし、ログに警告を出す
- [x] 不正な値を `Conf.cgi` へ保存しない
- [x] ゴールデンマスターテストを新しい挙動に合わせて書き直す

分担の理由と各担当の報告は
[archives/agents/TODO-027/](../agents/TODO-027/README.md) にある。

## きっかけ

TODO-024 で決めた方針にもとづく。対象は `search_n`・`todo_days`・
`year`/`month`/`day`・`date`・`cur_day` の 5 か所。`search_n=abc` や
`todo_days=abc` は `Conf.cgi` に残るので、一度踏むとトップページも
開けなくなる。読むときに既定値へ落とすだけでは直らないので、保存の側も
直す必要があった。

扱い方は TODO-012（不正な正規表現はその条件を無視して全件を出す）に
揃えた。

## やったこと

**表示する経路と、書き込む経路で、扱いを分けた。** ここが、着手前には
決まっていなかったところ。

### 表示する経路 — 既定値へ落として、警告を 1 行

`HandlerBase` に、引数の変換と検証を置いた。

| もの | 役目 |
|---|---|
| `convert_value()` | 変換できなければ `None` を返し、警告を 1 行出す |
| `str2date()` | ISO 8601 の文字列を、表示に使える日付にする |
| `check_date()` | `date_range()` の外なら `ValueError` |
| `date_range()` | 使える日付の範囲（日をずらす幅のぶん内側） |
| `check_int_range()` | 範囲外の整数なら `ValueError` |

`date_range()` と `check_int_range()` が要るのは、`datetime.date()` や
`datetime.timedelta()` が **`ValueError` ではなく `OverflowError`** を
投げるため。`month=99999999999` のような値は、`datetime` へ渡す前に
弾かないと拾えない。

`SEARCH_MODE_MAX_DAYS` は `MainHandler` から `HandlerBase` へ移した。
`date_range()` が使うため。

### 書き込む経路 — 400 で断る

`cmd=add`/`fix`/`update`/`del` で、`date`・`orig_date`・`time_start`・
`time_end` が**空でないのに読めない**ときは `HTTPError(400)`。
**書き込みが 1 つも起きる前に弾く。**

空のときの扱いは変えていない（`date` が空なら今日、`orig_date` が空なら
ToDo のファイル。TODO-016 の「空 ＝ 省略」）。

**表示と同じに扱ってはいけなかった。** 3 回目のレビューで見つかった。
`cmd=update&orig_date=2021-03-01&date=9999-12-31` を「読めないから
今日」と解釈すると、**利用者が指定していない日へ既存の予定が動く**。
以前は 500 で落ちていたので、書き込みは 1 つも起きなかった。
`orig_date` が読めないときに「消さずに足す」案も一度は実装したが、
同じ `sde_id` が 2 件できて、`del_sde()` / `get_sde()` が前提にしている
「ファイル内で `sde_id` は一意」が崩れる。**`del` で防いだはずの
消し間違いを `fix` 側で作っていた。**

400 にする前例は TODO-016 の「存在しない `sde_id` は 404」。
編集フォームからは起こらない入力なので、普通の操作は何も変わらない。

`get_time_arg()`（`time_start=abc` で 500）も同じ判断で塞いだ。
**これで、この経路に残っていた 500 は無くなった。**

`src/README.md` の `HandlerBase` の説明も直した。「`Conf.cgi` の
読み書き」だけでは、次に触る人が変換まわりを `MainHandler` に探しに
行く。

## テスト

`uv run pytest tests` が **380 件すべて通る**。`ruff format --check` /
`ruff check` / `basedpyright` / `mypy` もすべて通る。

`tests/test_web.py` の `TestInvalidUpdateArgs` を 14 件に書き直した。
`snapshot()`（`datadir` 以下の全ファイルの中身を dict で読む）を足して、
**400 のときに 1 行も変わっていないこと**を、日付ごとのファイルも
`ToDo.jsonl` もまとめて見ている。あわせて、正しい `orig_date` の削除・
更新と、空の `orig_date` の ToDo 削除が今までどおり効くことも、同じ
クラスに置いた（400 のガードが普通の操作を止めていないことが、その場で
読める）。

verifier が curl でも再現した。400 が返ること、`diff -r` で `datadir`
以下が変わらないこと、`cmd=fix` で別の日へ動かしても重複しないこと、
表示経路（`?date=abc` / `?search_n=abc` / `/edit?date=abc` など）は
200 のままであること。

## 4 往復かかった

実装 → 確認 → レビューを 4 回まわした。**振り返り:**

- **「読めない日付をどうするか」を、項目を立てる時点で聞けていなかった。**
  `CLAUDE.md` の「判断が要ることは、いま答えられるなら項目を立てる前に
  聞く」がまさにこれ。3 回目のレビューで論点が出てから利用者に聞いた
  ので、1 往復ぶん増えた
- **3 回目の implementer が `git checkout -- src` で未コミットの実装を
  一度消した。** 書き直しは丸ごと無駄。以降の依頼書には「作業ツリーを
  戻すコマンドは使わない」と明記した
- **reviewer は 3 回とも実質的な指摘を出した。** 特に 3 回目の
  「書き込む経路で既定値へ落とすと、データが動く」は、テストが通ることを
  見ても出てこない。TODO-017 で決めた「挙動や分岐が変わる項目には
  reviewer を入れる」が効いた例
- **3 回目の確認は `pytest` を走らせられなかった。** 原因は無関係な
  [TODO-033](TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)
  で、そちらを先に片付けてから 4 回目の確認をやり直した
