# TODO-027 verifier の報告（4 回目）

依頼書 (`verifier-request4.md`) のとおりに進めた。`git checkout` /
`git restore` / `git stash` は使っていない（`git status` / `git diff` は
読むだけ）。作業前に `git status` で、コミットされていないこと・
`tests/helpers.py` と `tests/test_webapp.py` に TODO-033 の
`DEF_URL_PREFIX` 対応がすでに入っていることを確認した。**結論として、
依頼書の項目はすべて実装者報告のとおりに動いた。不具合は見つからなかった。**

## 1. コマンド出力

`/home/ytani/work/ytsched` で個別に実行（`upgradeproject` は走らせて
いない）。

- `uv run ruff format --check --line-length 78 src tests`
  → 差分は `src/ytsched/__main__.py` の 1 か所だけ（コミット `2b4fcce`
  由来。TODO-027 の変更ファイルには差分無し）
- `uv run ruff check --extend-select I src tests` → `All checks passed!`
- `uv run basedpyright src tests` → `0 errors, 0 warnings, 0 notes`
- `uv run mypy src tests` → `Success: no issues found in 18 source files`
- `uv run pytest tests -q` → **`380 passed in 1.43s`**。TODO-033 で
  `tests/helpers.py` / `tests/test_webapp.py` が `DEF_URL_PREFIX` に
  追随したため、コレクション段階の全滅は解消し、**今回は本来の
  確認ができた**（3 回目はここが確認できなかった）

## 2. curl による再現（400・データ不変）

`--datadir` に一時ディレクトリ、ポート **8891**。`ToDo.jsonl` に
`sde_id=id-t` を 1 件、`2026/08/20.jsonl` に `sde_id=id-a` を 1 件
置いた状態から。`find $DATADIR -type f | xargs cat` で全ファイルの
中身を比べた（`diff` で無変化を確認）。

| 入力 | 結果 |
|---|---|
| `cmd=add&date=abc&title=t&sde_id=` | **400**・全ファイル無変化 |
| `cmd=add&date=9999-12-31&title=t&sde_id=` | **400**・同上 |
| `cmd=del&orig_date=abc&sde_id=id-t` | **400**・`ToDo.jsonl` 無事 |
| `cmd=update&orig_date=abc&date=2026-08-20&sde_id=id-a` | **400**・同上 |
| `cmd=update&orig_date=2026-08-20&date=9999-12-31&sde_id=id-a` | **400**・**元の予定（`id-a`）は動いていない**（`20.jsonl` 無変化） |
| `cmd=add&date=2026-08-21&time_start=abc&title=t&sde_id=` | **400**（500 でない）・無変化 |
| `cmd=add&date=2026-08-21&time_end=abc&title=t&sde_id=` | **400**・無変化 |
| `cmd=add&date=2026-08-21&time_start=25:00&title=t&sde_id=` | **400**・無変化 |

## 3. 正しい操作（念入りに確認）

同じサーバで続けて確認。

- **新規追加**: `cmd=add&date=2026-09-01&title=newitem&sde_id=` → 200、
  `2026/09/01.jsonl` に 1 件だけ入る
- **別の日へ移動**: `cmd=fix&orig_date=2026-09-01&date=2026-09-10&sde_id=<同ID>`
  → 200。元の `09/01.jsonl` は空になり、`09/10.jsonl` に**1 件だけ**
  （重複無し）
- **削除**: `cmd=del&orig_date=2026-09-10&sde_id=<同ID>` → 200、
  `09/10.jsonl` が空になった
- **ToDo 追加**（`sde_type=□ToDo`、`orig_date` 送らない）→ 200、
  `ToDo.jsonl` に追記、既存 `id-t` はそのまま
- **ToDo 修正**（`cmd=fix`、`orig_date` 送らない、`sde_id` は追加した
  ToDo のもの）→ 200、`ToDo.jsonl` は 2 行のまま（重複せず）、
  タイトルが書き換わった
- **ToDo 削除**（`cmd=del`、`orig_date` 送らない）→ 200、追加した ToDo
  が消え、`id-t` は残った
- **`date` を空で送る**（`cmd=add&date=&title=emptytoday&sde_id=`）→ 200、
  **今日のファイル**（`2026/08/23.jsonl`）に入った

いずれも実装者報告のとおりで、壊れていなかった。

## 4. 表示経路（GET）が既定値へ落ちる

`?date=abc` / `?cur_day=abc` / `?search_n=abc` / `?todo_days=abc` /
`?year=2021&month=13&day=1` / `/edit?date=abc` を叩き、**全部 200**。
書き込み経路とは別に、今までどおり 400 にしないことを確認した。

## 5. ログ

サーバのログ（`nohup` の出力）を `grep -iE "traceback|exception"` で
見た。**該当 0 件。** `grep -i warning` では、上記の各入力に対応する
`convert_value()` の警告が 1 行ずつ出ていた（例:
`date='abc': Invalid isoformat string: 'abc' .. ignored` /
`time_start='25:00': hour must be in 0..23, not 25 .. ignored`）。

## 6. サーバの停止

`pgrep -af "ytsched webapp --datadir <tmpdir>"` で PID（`uv run` 側
332763、実体の `python3` 側 332767）を確認してから両方 `kill`。
再度 `pgrep -af` で確認し、残っていないことを確認した（残った
プロセスは `pgrep` 自身の zsh ラッパのみ）。実データ
（`~/ytsched/data`）には触っていない。

`git status --short` は作業開始前と変わっておらず、報告ファイル
以外への書き込みは無い。

## main の判断が要る点

なし。依頼書の項目はすべて実装者報告のとおりに再現でき、不具合は
見つからなかった。3 回目で issue になっていた pytest のコレクション
全滅（`WebServer.URL_PREFIX`）は TODO-033 で解消しており、今回
`380 passed` を確認できた。
