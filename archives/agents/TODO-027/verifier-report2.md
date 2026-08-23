# TODO-027 verifier の報告（2 回目）

実装者の報告を鵜呑みにせず、依頼書どおりに自分で再現した。結論として、
すべて依頼書・実装者報告のとおりに動く。不具合は見つからなかった。

## 1. コマンド出力

`/home/ytani/work/ytsched` で個別に実行（`upgradeproject` は走らせていない）。

- `uv run ruff format --line-length 78 src tests`
  → `21 files left unchanged`（差分なし）
- `uv run ruff check --extend-select I src tests`
  → `All checks passed!`
- `uv run basedpyright src tests`
  → `0 errors, 0 warnings, 0 notes`
- `uv run mypy src tests`
  → `Success: no issues found in 18 source files`
- `uv run pytest tests`
  → `361 passed in 1.39s`（実装者報告の件数と一致。1 回目は 348、+13）

## 2. 表の再現（reviewer 指摘 1・2・4 の 6 通り）

一時ディレクトリ（scratchpad 配下、実データには触れていない）に
既存データと同じ形式（`docs/data-format.md` の JSON Lines）で
`2024/08/20.jsonl` を 1 件、`ToDo.jsonl` を 1 件（`SchedDataEnt` の
フィールド名に合わせた形）置いて `--datadir` に指定し、ポート 18127 で
バックグラウンド起動した。各入力の前に `Conf.cgi` を削除してから、
対象 URL → 素の GET (`/`) の順で curl し、`Conf.cgi` の有無を見た。

| 入力 | 1 回目 | 次の素の GET | `Conf.cgi` |
|---|---|---|---|
| `year=99999999999&month=1&day=1` | 200 | 200 | なし |
| `date=9999-12-31` | 200 | 200 | なし |
| `date=0001-01-01` | 200 | 200 | なし |
| `year=9999&month=12&day=31` | 200 | 200 | なし |
| `todo_days=99999999999` | 200 | 200 | なし |
| `todo_days=-99999999999` | 200 | 200 | なし |

6 通りすべて実装者報告のとおり。ToDo を 1 件置いた状態（実データがある
場合に指摘 2 が起きる、という reviewer の指摘の条件）でも 500 にならない
ことを確認した。

## 3. 1 回目の 8 通りが壊れていないか

`search_n=`（空）／`search_n=abc`／`todo_days=abc`／`year=abc`／
`month=13`／`day=32`／`date=abc`／`cur_day=abc` を同じ手順で叩き直した。
8 通りすべて 200 / 200 / `Conf.cgi` なし、で 1 回目と一致。

## 4. 正しい値が壊れていないか

- `Conf.cgi` を消してから `search_n=10` → 200、`Conf.cgi` に `SearchN\t10`
- 続けて `todo_days=7` → 200、`Conf.cgi` に `ToDo_Days\t7` が追記
- 続けて `todo_days=-1` → 200、`ToDo_Days\t-1`（off）に上書き
- `date=2021-01-02` / `year=2021&month=1&day=2` は両方 200
- `Conf.cgi` を消して `todo_days=7` を保存したあと `todo_days=99999999999`
  を叩いても `Conf.cgi` は `ToDo_Days\t7` のまま（`99999999999` で
  上書きされない）ことを確認した

## 5. 検索モード（5 年さかのぼる）

`search_str=ゾウガメ` で、2 年前（`2024-08-20`）に置いた予定
「ゾウガメ会議」が検索結果の HTML に実際に現れることを確認した
（`grep` ではなく取得した HTML の中身を見た）。

途中で 1 度、アプリ起動後にデータファイルを追加して検索したところ
0 件になったが、これは実装の不具合ではなく、**アプリ起動前に
データを置く必要がある**（起動時にデータを読み込む／インメモリの
キャッシュを持つ）ためだった。アプリを再起動してから同じデータで
検索すると見つかった。念のため記録しておく（TODO-027 の範囲外）。

## 6. 警告ログ

6 通りを再度叩き、ログに 1 行ずつ、何がどう不正だったか・使える範囲が
分かる形で出ていることを確認した。例外・トレースバックは無し
（`grep -i "traceback\|exception"` で WARNING 以外の行が無いことを確認）。

```
WARNING main_handler.py:280 convert_value()> year/month/day='99999999999/1/1': year must be in 1..9999, not 99999999999 .. ignored
WARNING main_handler.py:280 convert_value()> date='9999-12-31': date must be in 0005-12-31..9995-01-01, not 9999-12-31 .. ignored
WARNING main_handler.py:280 convert_value()> date='0001-01-01': date must be in 0005-12-31..9995-01-01, not 0001-01-01 .. ignored
WARNING main_handler.py:280 convert_value()> year/month/day='9999/12/31': date must be in 0005-12-31..9995-01-01, not 9999-12-31 .. ignored
WARNING main_handler.py:280 convert_value()> todo_days='99999999999': todo_days must be in -1..36500, not 99999999999 .. ignored
WARNING main_handler.py:280 convert_value()> todo_days='-99999999999': todo_days must be in -1..36500, not -99999999999 .. ignored
```

範囲（`0005-12-31..9995-01-01`）は `--days` 既定値 45 と
`SEARCH_MODE_MAX_DAYS`（5 年）から決まっており、1 回目の verifier 報告や
実装者報告の値と一致する。

## 7. サーバの停止

`pgrep -af "ytsched webapp --datadir <tmp>/v27-2-datadir"` で PID
（`uv run` 側と実体の `python3` 側の 2 個）を確認してから `kill` した。
再度 `pgrep -af` で確認し、残っていないことを確認した。

## 判断が要る点

見つからなかった。実装者報告・reviewer の指摘 1・2・4 に対する 2 回目の
修正は、コマンド出力・表の再現・既存動作の非破壊・警告ログのいずれも
報告どおりだった。

reviewer 報告に残っている「main の判断が要る点」（指摘 3 の
`TestConfArgs` の押さえが緩んだ件を TODO-028 に申し送るか、
`get_date_arg()`/`get_time_arg()`（POST 側）を別項目にするか）は、
本報告の対象外（依頼書に確認項目として挙がっていない）のため触れて
いない。
