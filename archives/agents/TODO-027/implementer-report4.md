# TODO-027 implementer の報告（4 回目）

依頼書 `implementer-request4.md` の 1・2・3 とテストの直しを実施した。
`git checkout` / `git restore` / `git stash` は使っていない
（読むのは `git diff` / `git status` / `git log` だけ）。
`tests/helpers.py` と `tests/test_webapp.py` には触っていない。
`mise run upgradeproject` は走らせていない。

---

## 変えたファイル

### `src/ytsched/main_handler.py`

- **`get_date_arg()`**（依頼書 1）: 空でないのに日付として読めない値
  （形式が不正、または `date_range()` の外）を
  `tornado.web.HTTPError(400, "invalid date: %s=%r", arg_name, value)`
  で断るようにした。空のときは今までどおり `None`。docstring に
  「書き込む経路専用」「なぜ既定値へ落とさないか」「`Raises`」を書いた
- **`get_time_arg()`**（依頼書 2）: `datetime.time.fromisoformat()` の
  素通しをやめ、`convert_value()` に載せた。空でないのに読めなければ
  `date` と同じ形で 400。**残っていた唯一の 500 が塞がった**
- **`exec_update()`**:
  - `orig_date_str` / `orig_date_is_broken` の二度読みを削除
    （依頼書の指摘 4）
  - `cmd in ["del", "fix", "update"]` の `if orig_date_is_broken:` 分岐と
    警告を削除し、`self.cmd_del(orig_date, sde_id)` の 1 行に戻した
  - 先頭のコメントを「400 は書き込みが起きる前に弾くので、
    `cmd_del()`/`cmd_add()` より先に引数を読む」という説明に書き換えた

**400 が書き込み前に返ることの根拠**: `get_date_arg("orig_date")` /
`get_date_arg("date")` / `get_time_arg("time_start")` /
`get_time_arg("time_end")` は 4 つとも `exec_update()` の冒頭にあり、
`cmd_del()` / `cmd_add()` はそのずっと後ろ。curl でも確かめた（後述）。

### `src/ytsched/handler.py`

**変更なし。** `convert_value()` をそのまま使えたため。

### `src/README.md`（依頼書 3）

- モジュール一覧の `handler.py` の行に「引数の変換と検証」を足した
- 「Web ハンドラ」節の `HandlerBase` の項に 3 行足した
  （`convert_value()` / `str2date()` / `check_date()` / `date_range()` /
  `check_int_range()` を列挙し、`TODO-027` を添えた）

依頼書のとおり書き換えすぎないようにし、既存の文はそのまま残した。

### `tests/test_web.py`

`TestInvalidUpdateArgs` を 400 の挙動に書き直した（7 件 → 14 件）。

共通の道具を 2 つ足した。

- `post_res(**args)` — POST してレスポンスをそのまま返す
  （`post_body()` は 200 を assert してしまうので使えない）
- `snapshot()` — `datadir` 以下の全ファイルの中身を dict で読む。
  **400 のときに 1 行も変わっていないこと**を、日付ごとのファイルも
  `ToDo.jsonl` もまとめて見るため

| テスト | 見ているもの |
|---|---|
| `test_add_with_unreadable_date_is_400` | `date=abc` → 400・`snapshot()` 不変・今日のファイルも `ToDo.jsonl` もできない |
| `test_add_with_far_future_date_is_400` | `date=9999-12-31` → 同上 |
| `test_del_with_unreadable_orig_date_is_400` | `cmd=del&orig_date=abc` → 400・元の予定が残る |
| `test_del_with_unreadable_orig_date_keeps_todo` | `ToDo.jsonl` を消しに行かない（消し間違い） |
| `test_del_with_unreadable_orig_date_logs_a_warning` | 400 に加えて警告が出る |
| `test_update_with_unreadable_orig_date_is_400` | 400・1 行のまま・重複しない |
| `test_far_future_orig_date_is_400` | `orig_date=9999-12-31` → 400・ToDo 無事 |
| `test_unreadable_time_start_is_400` | `time_start=abc` → **500 でなく 400**・データ無傷 |
| `test_unreadable_time_end_is_400` | `time_end=abc` → 同上 |
| `test_out_of_range_time_is_400` | `time_start=25:00` → 400 |
| `test_del_with_valid_orig_date_deletes` | 正しい `orig_date` の削除は今までどおり効く |
| `test_update_with_valid_orig_date_replaces` | 正しい `orig_date` の更新は今までどおり効く（1 行・title が変わる） |
| `test_del_todo_with_empty_orig_date_still_works` | **空**の `orig_date` は今までどおり ToDo を消す |

下の 3 件は reviewer の指摘 7「400 のガードが普通の操作まで止めて
いないことを、同じクラスの中で読めるようにする」に対応する。

`TestInvalidArgs`（GET の表示経路）には触っていない。

### `tests/test_main_handler.py`

**変更なし。** 落ちるものは無かった（このファイルの POST は
`TestExecUpdateDeadline` など、どれも正しい日付・時刻を渡している）。
実際に走らせて確かめた（後述）。

---

## 自分で確かめたこと

### 1. 静的チェック

`upgradeproject` は走らせていない。

| コマンド | 結果 |
|---|---|
| `uv run ruff format --line-length 78 src/ytsched/main_handler.py tests/test_web.py` | `2 files left unchanged` |
| `uv run ruff format --line-length 78 --diff src tests` | 差分は `src/ytsched/__main__.py` の 1 か所だけ（`2b4fcce` 由来。TODO-027 の変更ファイルには差分なし。触っていない） |
| `uv run ruff check --extend-select I src tests` | `All checks passed!` |
| `uv run mypy src tests` | `Found 3 errors in 2 files` — **すべて既知の `WebServer.URL_PREFIX`**（`tests/helpers.py:23`, `tests/test_webapp.py:30,34`）。増えていない |
| `uv run basedpyright src tests` | `3 errors` — 同じ 3 件だけ |
| `uv run mypy src` / `uv run basedpyright src` | どちらもエラー 0 |

### 2. pytest — **通常の `uv run pytest` は走らせられない**

依頼書のとおり、`tests/helpers.py:23` の `WebServer.URL_PREFIX` で
コレクションが全滅するため、**そのままでは 1 件も走らない。**
これは直していない。

**そのうえで、リポジトリのファイルを一切変えない回避策で走らせてみた。**
scratchpad に置いた pytest プラグイン 1 個だけを使う。

```python
# /tmp/.../scratchpad/urlfix.py（リポジトリの外）
from ytsched.webapp import WebServer

if not hasattr(WebServer, "URL_PREFIX"):
    WebServer.URL_PREFIX = WebServer.DEF_URL_PREFIX
```

```
PYTHONPATH=<scratchpad> uv run pytest \
  tests/test_web.py tests/test_main_handler.py \
  tests/test_handler.py tests/test_ytsched.py -p urlfix -q
→ 1 failed, 300 passed
```

唯一の失敗は `tests/test_handler.py::test_conf_is_not_locale_dependent`
で、**サブプロセスを起こすテストなのでプラグインが効かず、同じ
`URL_PREFIX` の AttributeError で落ちている**（TODO-027 とは無関係）。

**これは「テストが通った」という報告ではない。** 素の
`uv run pytest` は今も全滅するので、`tests/helpers.py` が直るまで
本来の確認はできない。上は「自分の書いたテストが、自分の書いた実装で
実際に成立するか」を手元で見ただけのもの。**判断は main に任せる。**

（この回避策は自分の手元だけのもので、リポジトリには何も置いていない。
`tests/` 以下も `.claude/` 以下も触っていない。）

### 3. 実際に動かした（curl）

`--datadir` に scratchpad の一時ディレクトリ、ポート 18274。
`ToDo.jsonl` に `sde_id=id-t` を 1 件だけ置いた状態から。

| 入力 | 結果 |
|---|---|
| `cmd=add&date=abc` | **400**・ファイルが 1 つもできない |
| `cmd=add&date=9999-12-31` | **400**・同上 |
| `cmd=add&date=2026-09-02&time_start=abc` | **400**（前は 500）・同上 |
| `cmd=add&date=2026-09-02&time_end=25:00` | **400**・同上 |
| `cmd=del&sde_id=id-t&orig_date=abc` | **400**・`ToDo.jsonl` 無傷 |
| `cmd=add&date=2026-09-05&time_start=09:00&time_end=10:00` | 200・`2026/09/05.jsonl` に 1 件 |
| `cmd=fix&orig_date=2026-09-05&date=2026-09-06` | 200・05 が空になり 06 に 1 件（重複なし） |
| `cmd=del&orig_date=2026-09-06` | 200・06 が空 |
| `cmd=add&date=`（空） | 200・**今日**のファイル（`2026/08/23.jsonl`） |
| `cmd=del&sde_id=id-t&orig_date=`（空） | 200・ToDo が消える |
| `GET /?date=abc` | **200**（表示経路は今までどおり既定値へ落ちる） |
| `GET /edit?date=abc` | **200**（同上） |

サーバのログを `grep -iE "warning|error|traceback|exception"` で見た。
**トレースバック・例外は 1 つも無し。** 警告は `convert_value()` の
1 行ずつだけ。

サーバは `pgrep -af` で PID を確かめてから kill し、消えたことを
確認した。実データ（`~/ytsched/data`）には触っていない。

### 4. `datetime.time.fromisoformat()` の例外（依頼書の「念のため確かめる」）

`abc` / `25:00` / `99999999999` / `1e999` / `:` / 400 桁の数字を
渡して確かめた。**全部 `ValueError`。`OverflowError` は出ない。**
`check_int_range()` のような下ごしらえは要らない。

---

## 単独で決めた判断

1. **`get_date_arg()` / `get_time_arg()` に `strict` のようなフラグを
   足さず、無条件に 400 を投げる形にした。**
   この 2 つの呼び出し元は `exec_update()` の 4 か所だけで
   （`grep` で確認）、表示経路の `get_date()` は
   `convert_value()` を直接呼んでいて別系統だから。フラグを足すと、
   「読めない値を既定値へ落とす」経路が呼び出し元に無いのに残る。
   docstring に「書き込む経路専用」と明記した
2. **`HTTPError` のメッセージは
   `"invalid date: %s=%r", arg_name, value` の形にした。**
   前例（`main_handler.py:454` の 404）が `%s` と引数を分けて渡す
   Tornado の書き方なので、それに揃えた
3. **`orig_date`・`date`・`time_start`・`time_end` の 4 つを同じ扱いに
   した。** 依頼書 1 は `date`・`orig_date`・`time_*` を挙げていたので
   そのとおり。`deadline_*` はパースしないので対象外
4. **`test_del_with_unreadable_orig_date_logs_a_warning` を残した。**
   `not deleted` の警告は消えたが、`convert_value()` の
   `orig_date='abc': Invalid isoformat string ... ignored` が出るので、
   assert を `"orig_date='abc'"` だけに絞って残した。「黙って断らない」
   ことは押さえておきたかった
5. **`pytest.mark.parametrize` を使うのをやめた。**
   `WebTestBase` は `AsyncHTTPTestCase`（`unittest.TestCase`）なので
   parametrize が効かず、`TypeError` になった（実際に落ちた）。
   `assert_unreadable_time_is_400()` という補助メソッドを作って、
   `time_start` / `time_end` の 2 件から呼ぶ形にした。
   理由をその docstring に書いた
6. **回避策の pytest プラグインは scratchpad にだけ置いた。**
   `conftest.py` をリポジトリに置けば楽だが、それは
   `tests/helpers.py` 側の別項目に手を出すことになるので避けた

---

## 気づいたが直さなかったもの

1. **`convert_value()` の警告が `.. ignored` で終わる。**
   書き込む経路では「無視した」のではなく「400 で断った」なので、
   文言が実態と合わなくなった。ただし `convert_value()` は表示経路
   （そこでは `ignored` が正確）と共用で、直すなら
   ・表示経路の文言も変える ・400 の側で 2 行目を出す
   のどちらかになる。どちらも今回の範囲を超えると判断して、
   **文言はそのままにした。main の判断を仰ぎたい**
2. **`tests/helpers.py:23` / `tests/test_webapp.py:30,34` の
   `WebServer.URL_PREFIX`。** 依頼書のとおり触っていない。別項目
3. **`src/ytsched/__main__.py` の `ruff format` 差分。**
   `2b4fcce` 由来で TODO-027 とは無関係。触っていない
4. **`del_sde()` が、見つからなくても `save()` を呼んで空ファイルを
   作る**（reviewer の指摘 9）。TODO-005 の頃からの挙動で、この項目の
   範囲外。今回 `test_del_with_valid_orig_date_deletes` が
   「削除後にファイルが空文字になる」ことを固定したので、
   もしこれを変えるならこのテストも直すことになる
5. **`SEARCH_MODE_MAX_DAYS` の名前と場所の対応**（reviewer の指摘 5）・
   **`--days` を極端に大きくしたときの `date_range()`**（指摘 6）。
   どちらも reviewer が「この項目でやることではない」と書いたとおり、
   触っていない

---

## うまくいかなかったところ

- **`uv run pytest` を素の状態で走らせられなかった。** 上記のとおり
  `tests/helpers.py` が原因で、依頼書で「直すな」と指示されている。
  回避策で走らせた結果は書いたが、**本来の確認は済んでいない**
- 最初 `pytest.mark.parametrize` で `time_start`/`time_end` をまとめよう
  として `TypeError` で落ちた（判断 5 のとおり書き直した）
