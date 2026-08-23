# TODO-027 verifier の報告（3 回目）

依頼書 (`verifier-request3.md`) のとおりに、`git diff` は読むだけにして、
自分で curl を叩き直して確かめた。結論として、**依頼書に挙げられた
入力・操作はすべて実装者報告のとおりに動いた。不具合は見つからなかった。**

ただし、**`uv run pytest tests` は「TODO-027 の変更とは無関係な原因」で
コレクションの段階から全滅している。** これは main の判断が要る点として
末尾に書く。

作業前に `git status` で、コミットされていないことと変更ファイルが
実装者報告と一致することを確認した（`TODO.md` /
`src/ytsched/{edit_handler,handler,main_handler}.py` /
`tests/{test_main_handler,test_web}.py`）。`git checkout` 等の
作業ツリーを戻すコマンドは使っていない。

## 1. コマンド出力

`/home/ytani/work/ytsched` で個別に実行（`upgradeproject` は走らせていない）。

- `uv run ruff format --line-length 78 --diff src tests`
  → `1 file would be reformatted, 20 files already formatted`。
  差分があるのは `src/ytsched/__main__.py` の 1 か所（`webapp()` の
  引数の折り返し）だけで、**TODO-027 の変更ファイルには差分無し**。
  `--diff` を使ったのは、ファイルを書き換えないため（このリポジトリでは
  ソースを直さないのが自分の役目なので）
  ※依頼書どおりの `ruff format`（書き込みあり）は権限（auto mode の
  classifier）に拒否されたため、`--diff` で代用した
- `uv run ruff check --extend-select I src tests`
  → `All checks passed!`
- `uv run basedpyright src tests`
  → **3 errors**。すべて `tests/helpers.py:23`・`tests/test_webapp.py:30,34`
  の `WebServer.URL_PREFIX にアクセスできません`（`reportAttributeAccessIssue`）
- `uv run mypy src tests`
  → **Found 3 errors in 2 files**。同じ箇所（`WebServer` に `URL_PREFIX`
  属性が無い、`DEF_URL_PREFIX` の間違いでは、というメッセージ）
- `uv run pytest tests`
  → **4 errors during collection**（`tests/test_handler.py` /
  `test_main_handler.py` / `test_web.py` / `test_ytsched.py` の 4 ファイル
  すべてが `tests/helpers.py:23` の
  `AttributeError: type object 'WebServer' has no attribute 'URL_PREFIX'.
  Did you mean: 'DEF_URL_PREFIX'?` で import に失敗し、**1 件も実行され
  ないまま `Interrupted: 4 errors during collection`**

**この 3 つの失敗は同じ原因。** `tests/helpers.py:23` の
`URL_PREFIX = WebServer.URL_PREFIX` が、既に存在しない属性を読んでいる。

```
$ grep -rn "URL_PREFIX" src/ytsched/webapp.py
34:    DEF_URL_PREFIX = "/ytsched"
```

`src/ytsched/webapp.py`（`URL_PREFIX` → `DEF_URL_PREFIX` に変わった側）も
`tests/helpers.py`（読む側）も、**どちらも TODO-027 の `git diff` には
含まれていない**（`git status` で未変更）。`git log` で確認したところ:

- `tests/helpers.py` の最終コミットは 2026-08-20（`URL_PREFIX` を素朴に
  参照する形のまま）
- `src/ytsched/webapp.py` の最終コミットは 2026-08-23 03:05（コミット
  `2b4fcce feat(webapp): add url_prefix option`。`DEF_URL_PREFIX` へ改名）

実装者報告 3 回目（タイムスタンプ 2026-08-21 21:03）の時点では、まだ
`2b4fcce` が develop に入っていなかったと見られる。つまり、
**TODO-027 の 3 回目の実装が終わったあとに、別の作業（url_prefix 機能、
おそらく TODO-029 系）が develop へマージされ、その副作用で
`tests/helpers.py` が壊れた。** TODO-027 の diff 自体に原因は無い。

このため、**実装者報告にある「374 passed」を、今の作業ツリーでは
再現できなかった**（pytest がコレクションで止まるため）。

## 2. 依頼書の表の再現（`--datadir` に一時ディレクトリ、`ToDo.jsonl` に 1 件）

`/tmp/claude-649/…/scratchpad/v27-3-datadir` に
`2024/08/20.jsonl`（予定 1 件）と `ToDo.jsonl`（ToDo 1 件、`sde_id=id-t`）を
`docs/data-format.md` の形式で置き、ポート 18227 で起動して curl した。

| 入力 | 結果 |
|---|---|
| `?year=2021&month=99999999999&day=1` | 200 |
| `?year=2021&month=1&day=99999999999` | 200 |
| `?year=2021&month=1&day=-99999999999` | 200 |
| `?year=2021&month=13&day=1` | 200 |
| `/edit?date=abc` | 200・フォームに今日の日付 `value="2026-08-23"` が入る |
| `/edit?date=9999-12-31` | 200・同上 |
| `?cmd=add&date=abc&title=test1&sde_id=` | 200・**今日のファイル**（`2026/08/23.jsonl`）に `test1` が追加。`ToDo.jsonl` は無変更 |
| `?cmd=add&date=9999-12-31&title=test2&sde_id=` | 200・同じ今日のファイルへ `test2` が追記（2 行目）。`ToDo.jsonl` は無変更 |
| `?cmd=del&orig_date=abc&sde_id=id-t` | 200・**`ToDo.jsonl` は無事**（`id-t` は消えていない） |

実装者報告の表・依頼書の期待どおり。すべて実装者報告と一致した。

## 3. 1・2 回目に確かめたものの回帰

同じサーバで叩き直した。

| 入力 | 結果 |
|---|---|
| `search_n=abc` | 200 |
| `todo_days=abc` | 200 |
| `todo_days=99999999999` | 200 |
| `date=9999-12-31` | 200 |

4 通りとも 200。壊れていない。

## 4. 正しい操作（データを書き込む経路。念入りに確認）

- **新規追加**: `cmd=add&date=2025-01-10&title=normal1&sde_id=` → 200、
  `2025/01/10.jsonl` に `normal1` が 1 件だけ入る
- **別の日へ移動**（`cmd=fix&orig_date=2025-01-10&date=2025-02-15&sde_id=<同じID>`）
  → 200。**元の `2025/01/10.jsonl` は空になり**（`sde_id` を検索してもヒット
  無し）、**新しい `2025/02/15.jsonl` に 1 件だけ**入った（重複無し）
- **削除**（`cmd=del&orig_date=2025-02-15&sde_id=<同じID>`）→ 200、
  `2025/02/15.jsonl` が空になった
- **ToDo の追加**（`sde_type=□ToDo` を付け、`orig_date` は送らない）
  → 200、`ToDo.jsonl` に新しい ToDo が 1 件追記され、既存の `id-t` は
  そのまま残った
- **ToDo の修正**（同じ `sde_id`、`cmd=fix`、`orig_date` は送らない）
  → 200、`ToDo.jsonl` の中身が書き換わり（`title=todo-fixed`）、
  **重複せず 2 行のまま**（既存 `id-t` ＋ 更新後の ToDo）
- **ToDo の削除**（`cmd=del&sde_id=<同じID>`、`orig_date` は送らない）
  → 200、`ToDo.jsonl` から消え、**`id-t` は残った**（消し間違い無し）

いずれも普通の操作の順（ブラウザから叩くのと同じ形）で確認し、
実装者報告のとおり壊れていなかった。

（最初に ToDo 追加を試したとき、`type=` というクエリを送って `sde_type=`
を送っていなかったため、日付ベースのファイルへ入る挙動になった。これは
自分のパラメータ名の間違いで、実装のバグではない。`sde_type=□ToDo` で
送り直したら意図どおり `ToDo.jsonl` へ入った。）

## 5. 警告ログ

サーバのログ（`nohup` の出力）を `grep -iE "warning|traceback|exception"`
で見た。**トレースバック・例外は無し。** 警告は依頼書の入力それぞれに
対応する 1 行ずつが出ていた（一部抜粋）。

```
WARNING handler.py:151 convert_value()> year/month/day='2021/99999999999/1': month must be in 1..12, not 99999999999 .. ignored
WARNING handler.py:151 convert_value()> year/month/day='2021/1/99999999999': day must be in 1..31, not 99999999999 .. ignored
WARNING handler.py:151 convert_value()> year/month/day='2021/1/-99999999999': day must be in 1..31, not -99999999999 .. ignored
WARNING handler.py:151 convert_value()> year/month/day='2021/13/1': month must be in 1..12, not 13 .. ignored
WARNING handler.py:151 convert_value()> date='abc': Invalid isoformat string: 'abc' .. ignored
WARNING handler.py:151 convert_value()> date='9999-12-31': date must be in 0005-12-31..9995-01-01, not 9999-12-31 .. ignored
WARNING handler.py:151 convert_value()> orig_date='abc': Invalid isoformat string: 'abc' .. ignored
WARNING main_handler.py:896 exec_update()> orig_date='abc': unknown file .. not deleted
WARNING handler.py:151 convert_value()> search_n='abc': invalid literal for int() with base 10: 'abc' .. ignored
WARNING handler.py:151 convert_value()> todo_days='abc': invalid literal for int() with base 10: 'abc' .. ignored
WARNING handler.py:151 convert_value()> todo_days='99999999999': todo_days must be in -1..36500, not 99999999999 .. ignored
```

`convert_value()` が `handler.py` に出ているのは、実装者報告のとおり
`HandlerBase` へ移った結果で、想定どおり。

## 6. サーバの停止

`pgrep -af "ytsched webapp --datadir <tmpdir>"` で PID（`uv run` 側と
実体の `python3` 側の 2 個、298622 / 298627）を確認してから `kill` した。
再度 `pgrep -af` で確認し、残っていないことを確認した。

## main の判断が要る点

1. **`uv run pytest tests` が現状、コレクションの段階で全滅する
   （4 errors during collection、0 tests run）。** 原因は
   `tests/helpers.py:23` の `WebServer.URL_PREFIX`（存在しない属性。
   `DEF_URL_PREFIX` に改名済み）で、`basedpyright`・`mypy` も同じ箇所で
   3 件ずつエラーを出す。**TODO-027 の `git diff` には
   `tests/helpers.py` も `src/ytsched/webapp.py` も含まれておらず、
   原因は TODO-027 の変更ではない。** `git log` から、TODO-027 の
   3 回目の実装（2026-08-21）のあとに `2b4fcce feat(webapp): add
   url_prefix option`（2026-08-23、develop へマージ済み）が入り、
   その副作用と見られる。**TODO-027 をこの状態のままコミットしてよいか、
   先に `tests/helpers.py` 側を直す（別項目にする、または今のうちに
   拾う）かは main の判断。** 現状のままだと、TODO-027 をコミットしても
   `pytest` は通らない
2. curl での機能確認（依頼書の 2〜4）は**すべて実装者報告のとおりで、
   不具合は見つからなかった**。ここは判断不要
