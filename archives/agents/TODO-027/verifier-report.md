# TODO-027 verifier の報告

依頼書どおりに、実装者の報告を鵜呑みにせず自分で再現した。結論として、
すべて依頼書・実装者報告のとおりに動く。不具合は見つからなかった。

## 1. コマンド出力

`/home/ytani/work/ytsched` で個別に実行（`upgradeproject` は走らせていない）。

- `uv run ruff format --line-length 78 --diff src tests`
  → `21 files already formatted`（差分なし）
- `uv run ruff check --extend-select I src tests`
  → `All checks passed!`
- `uv run basedpyright src tests`
  → `0 errors, 0 warnings, 0 notes`
- `uv run mypy src tests`
  → `Success: no issues found in 18 source files`
- `uv run pytest tests`
  → `348 passed in 1.35s`（実装者報告の件数と一致）

## 2. git diff の確認

`git diff src/ytsched/main_handler.py` を読み、実装者報告の記述
（`convert_value[T]()` / `get_conf_arg[T]()` / `ymd2date()` の追加、
`Callable` は `collections.abc` から import、PEP 695 のジェネリック）と
一致していることを確認した。`tests/test_web.py` / `tests/test_main_handler.py`
も報告どおりの変更（`TestInvalidArgs` の追加、`date_id()` の移動）。

## 3. 起動して curl で叩いた（表の再現）

一時ディレクトリ（scratchpad 配下、実データには触れていない）を
`--datadir` に指定し、ポート 18027 でバックグラウンド起動した。

```
uv run ytsched webapp --datadir <tmp>/v27-datadir --port 18027 > <tmp>/v27-app.log 2>&1 &
```

各入力の前に `Conf.cgi` を削除してから、対象 URL → 素の GET (`/`) の
順で curl し、`Conf.cgi` の有無を見た。

| 入力 | 1 回目 | そのあとの素の GET | `Conf.cgi` |
|---|---|---|---|
| `search_n=`（空） | 200 | 200 | なし |
| `search_n=abc` | 200 | 200 | なし |
| `todo_days=abc` | 200 | 200 | なし |
| `year=abc`（＋`month=1&day=1`） | 200 | 200 | なし |
| `month=13`（＋`year=2021&day=1`） | 200 | 200 | なし |
| `day=32`（＋`year=2021&month=1`） | 200 | 200 | なし |
| `date=abc` | 200 | 200 | なし |
| `cur_day=abc` | 200 | 200 | なし |

8 通りすべて、実装者報告のとおり 200 / 200 / `Conf.cgi` 作られず、を
自分で再現できた。

## 4. `Conf.cgi` に不正値が既に入っている状態

`printf 'SearchN\tabc\nToDo_Days\tabc\n' > Conf.cgi` としてからトップ
ページを取得し、HTTP 200 を確認。取得した HTML を解析し、

- `search_n` の hidden input が `value="5"`（`DEF_SEARCH_N` の既定値）
- `todo_days` の `<select>` 内で `selected` が付いた `<option>` が
  `value="365"`（既定値）

であることを、grep ではなく HTML を実際にパースして確かめた（実装者
報告の値と一致）。

## 5. 正しい値が壊れていないこと

- `Conf.cgi` を消してから `?search_n=10&todo_days=7` を叩くと 200、
  `Conf.cgi` の中身は `SearchN\t10` / `ToDo_Days\t7`
- 続けて `?search_n=abc&todo_days=abc` を叩いても 200 で、`Conf.cgi`
  の中身は書き換わらず `10` / `7` のまま（不正値で上書きされない）
- `?date=2021-01-02` と `?year=2021&month=1&day=2` は両方 200

## 6. 警告ログ

`v27-app.log` に、不正値ごとに何がどう不正だったかが分かる形で
1 行ずつ出ていることを確認した（例外・トレースバックは無し）。

```
WARNING main_handler.py:274 convert_value()> search_n='': invalid literal for int() with base 10: '' .. ignored
WARNING main_handler.py:274 convert_value()> search_n='abc': invalid literal for int() with base 10: 'abc' .. ignored
WARNING main_handler.py:274 convert_value()> todo_days='abc': invalid literal for int() with base 10: 'abc' .. ignored
WARNING main_handler.py:514 ymd2date()> year='abc', month='1', day='1': invalid literal for int() with base 10: 'abc' .. ignored
WARNING main_handler.py:514 ymd2date()> year='2021', month='13', day='1': month must be in 1..12, not 13 .. ignored
WARNING main_handler.py:514 ymd2date()> year='2021', month='1', day='32': day 32 must be in range 1..31 for month 1 in year 2021 .. ignored
WARNING main_handler.py:274 convert_value()> date='abc': Invalid isoformat string: 'abc' .. ignored
WARNING main_handler.py:274 convert_value()> cur_day='abc': Invalid isoformat string: 'abc' .. ignored
WARNING main_handler.py:274 convert_value()> ToDo_Days='abc': invalid literal for int() with base 10: 'abc' .. ignored
WARNING main_handler.py:274 convert_value()> SearchN='abc': invalid literal for int() with base 10: 'abc' .. ignored
```

`grep -i "traceback\|error\|exception"` を WARNING 除外で実行し、
例外・トレースバックが無いことも確認した。

## 7. サーバの停止

`pgrep -af "ytsched webapp --datadir <tmp>"` で PID (`uv run` 側と
実体の `python3` 側の 2 個) を確認してから `kill` した。
`pgrep -af "ytsched webapp"` で再確認し、プロセスが残っていないこと
（マッチしたのは自分のシェルコマンド文字列自体のみ）を確認した。

## 判断が要る点

- 見つからなかった。実装者が「単独で決めた判断」に挙げている
  「引数の落とし先を `Conf.cgi` の値経由にした（`DEF_SEARCH_N` へ
  直行しない）」件は、その判断で確かに `Conf.cgi` 保存済みの値が
  守られることを 5. で確認済み。ここは main の判断（依頼書の文面との
  整合）のみが要る点で、動作としては報告どおり。
