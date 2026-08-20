# TODO-006 verifier 報告

implementer の報告（`archives/agents/TODO-006/implementer-report.md`）は
参考にしたが、値は**自分で実行し直して**確かめた。

## 1. 静的チェック・テスト

| コマンド | 結果 |
| --- | --- |
| `uv run pytest tests -q` | **161 passed**（5.15s） |
| `uv run mypy src tests` | **2 errors**。`ytsched.py:357` と `__main__.py:22` の `Name "__class__" is not defined`（既知・TODO-007 の範囲）のみ |
| `uv run basedpyright src tests` | **0 errors, 0 warnings, 0 notes** |
| `uv run ruff check --extend-select I src tests` | **Found 87 errors.**（既知・TODO-015 / TODO-008 の範囲。実装者報告の 87 件と一致） |

3 つとも実装者の報告どおり。新しい種類の ruff 指摘が増えていないことは
件数の一致で確認した（個別種別までは数え直していないが、97→87 で
implicit-optional 分 10 件減という説明と矛盾しない）。

## 2. webapp 起動確認

```
uv run ytsched webapp --datadir <一時dir> --port 10199
```

- `GET /ytsched/` → **200**
- `GET /ytsched/edit` → **200**
- `GET /ytsched/edit?todo_flag=true` → **200**
- `curl` で取得した HTML に `{{` `{%` の生残りなし（grep 0 件）
- サーバログ（stdout/stderr をリダイレクトしたファイル）に
  `traceback` / `error` / `exception` の出力なし
  （出ていたのは起動ログ 1 行のみ）
- 終了後、`pgrep -f "ytsched webapp --datadir"` で PID が残っていない
  ことと、ポートへの接続が拒否される（`000`）ことを確認して停止済み

**補足（依頼文の見落としに注意）:** `/ytsched/edit` は GET も POST も
実質 `EditHandler.get()`（編集画面の表示）にしかならず、実際の
add/update/del は **`/ytsched/`（`MainHandler`）へ `cmd` パラメータ付きで
POST する**構成。最初 `/ytsched/edit` に POST して確かめようとしたら
ファイルが 1 つも書かれず、`/ytsched/` に POST し直したら書かれた。
実装バグではなく元々の URL 構成（`webapp.py` のルーティング）どおり。

## 3. データ形式（実際に一時 datadir へ POST して確認）

`/ytsched/` へ `cmd=add` を 4 回 POST（時刻あり／時刻なし／終了時刻だけ
空／ToDo）、続けて `cmd=update`、`cmd=del` を実行し、`cat -A` で確認。

`2026/08/20.cgi`（`cat -A`、タブは `^I`、末尾 `$` は改行）:

```
6b507846-...^I2026/08/20^I05:45-:^I^I<買い物>^I^I$
d075784f-...^I2026/08/20^I09:05-10:30^I^I<会議>^I^I$
3df4d38a-...^I2026/08/20^I:-:^I^I<時刻なし>^I^I$
```

- 7 項目のタブ区切り、時刻なしは `:-:`、時刻ありは `09:05-10:30`、
  終了時刻だけ空は `05:45-:` — **いずれも従来どおりの形**
- `ToDo.cgi` も同じ 7 項目の形（`sde_type` に `□`、時刻欄は `:-:`）
- `cmd=update`（日付を 08/20 → 08/21、時刻を 11:00-12:00 に変更）で
  行が 20.cgi から消え、21.cgi に正しい内容で移動することを確認
- `cmd=del` で 21.cgi の行が消え、ファイルは空になることを確認
  （`.bak` ファイルが作られる挙動も従来どおり）

データ形式・書き込み経路とも壊れていない。

## 4. 実装者が独断で決めた 2 点の呼び出し箇所の網羅

### `exec_update()` の戻り値型を `tuple[datetime.date | None, str | None]` に

呼び出し箇所は `main_handler.py:135` の 1 か所のみ（`grep -rn`
で確認）。受け取った `modified_date` / `modified_sde_id` の使われ方を
136〜189 行で追った:

- `self._sd.get_sdf(modified_date)` — `get_sdf()` の引数は
  `date: datetime.date | None = None` なので `None` を受けても問題ない
- `sdf.get_sde(modified_sde_id)` — 戻り値 `SchedDataEnt | None` を
  `if sde is not None:` で分岐しており、`None` が来ても安全
- `if modified_date:` で falsy（`None` 含む）を弾いてから使っている

呼び出し側は `None` を受けても壊れない。実際に `cmd=del` を POST して
（`modified_sde_id` が `None` になる経路）200 が返り、例外も出ていない
ことも確認済み（上記 3.）。

### `SchedData.add_sde()` の既定値を外した件

`grep -rn "add_sde("` で `src` と `tests` を網羅した結果:

- `SchedData.add_sde(date, sde)`（`ytsched.py:715`）の呼び出しは
  `main_handler.py:635, 637` と `tests/test_ytsched.py:704, 712, 720`
  の **計 5 か所、すべて 2 引数の位置引数**。実装者報告と一致
- なお `SchedDataFile.add_sde(sde)`（別メソッド、`ytsched.py:529`）は
  元々引数 1 個で既定値も無く、今回の変更の対象外。呼び出しは
  `tests/test_ytsched.py` と `tests/test_web.py`（テストヘルパー内、
  別物の `add_sde` メソッド）に複数あるが、いずれも影響なし

pytest 161 passed で実際にこの経路も通っている。

## 結論

依頼の確認項目はすべて再現でき、implementer の報告と食い違いは無かった。
不具合は見つからなかった。

main の判断が要る点は implementer 報告と同じ 2 点（`exec_update()` の
戻り値型、`add_sde()` の既定値除去）。verifier としては、どちらも
呼び出し箇所を網羅した上で「壊れていない」ことを確認済み。

## 6. 追加変更の再検証（2 回目）

reviewer の指摘（1-1: `sde is None` 時の warning 追加、1-2: `SchedData`
docstring の型修正）を main が反映した後、再度自分で実行し直して確認した。

### 静的チェック・テスト

| コマンド | 結果 |
| --- | --- |
| `uv run pytest tests -q` | **161 passed**（5.00s、変化なし） |
| `uv run mypy src tests` | **2 errors**（`__class__` の 2 件のみ、変化なし） |
| `uv run basedpyright src tests` | **0 errors, 0 warnings, 0 notes**（変化なし） |
| `uv run ruff check --extend-select I src tests` | **Found 87 errors.**（変化なし） |
| `uv run ruff format --line-length 78 --check src tests` | **13 files already formatted** |
| 78 文字超の行 | `awk 'length > 78' src/ytsched/*.py tests/*.py` で **0 件** |

新しい種類の指摘は増えていない。

### webapp 起動確認

一時 datadir・`--port 10200` で起動。`GET /ytsched/` → **200**、
`GET /ytsched/edit` → **200**。従来どおり。

### warning が出ることの確認

reviewer の指摘どおりの経路（`date` を空にして、ToDo ではない
`sde_type` の予定を `cmd=add` で `/ytsched/` へ POST）を一時 datadir で
再現した。

```
curl -d "cmd=add&sde_id=&date=&time_start=&time_end=&sde_type=&title=空日付&place=&detail=" http://localhost:10200/ytsched/
```

- HTTP ステータス: **200**（従来どおり）
- サーバログに次の warning が出た:

```
WARNING handler.py.MainHandler.get:153> sde not found: modified_date=2026-08-20, modified_sde_id=6baf0640-f8a4-4fd6-89d2-7ff60cc83071 (cmd=add)
```

**この経路で warning が出るしくみも実際にファイルを見て確認した。**
`date` が空だと `cmd_add()` 内で `SchedDataEnt` の `date` はコンストラクタで
今日の日付に既定されるが、ToDo でない場合の書き込み先は
`self._sd.add_sde(date, new_sde)` の `date`（POST された生の `None`）で
決まるため、実体は `ToDo.cgi` に書かれる
（`ToDo.cgi` の中身: `6baf0640-...\t2026/08/20\t:-:\t\t空日付\t\t`）。
一方 `exec_update()` が返す `modified_date` は `new_sde.date`
（今日の日付、`None` ではない）になるので、`get()` 側は
今日の日付ファイル（`2026/08/20.cgi`。実際には作られず存在しない）を
探しに行き、見つからず `sde is None` になって warning が出る。
これは依頼にある既知の根本原因（TODO-016 送り）どおりの経路で、
今回の warning はその経路を検知して記録する分だけの変更であり、
狙いどおり動いている。

終了後、`pgrep -f "ytsched webapp"` でプロセスが残っていないことを
確認して停止済み。

### 結論

reviewer 指摘への追加対応 2 点とも、依頼どおりの動作を確認した。
新たな不具合は見つからなかった。
