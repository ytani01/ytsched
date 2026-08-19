# TODO-003 verifier の報告

## 1. `uv sync`

○ 通った。

```
$ uv sync
Resolved 11 packages in 0.69ms
Checked 10 packages in 0.13ms
```

版数: pytest 9.1.1 / pytest-cov 7.1.0（report-implementer.md と一致）。

## 2. `uv run pytest`

○ 通った。**140 passed, 6 xfailed**（約2.4秒）。report-implementer.md の
数字と一致。

```
$ uv run pytest
tests/test_handler.py ......x...x                                [  7%]
tests/test_web.py ...............................                [ 28%]
tests/test_webapp.py ....x                                       [ 32%]
tests/test_ytsched.py .................................          [ 66%]
...................xx...........................x                [100%]
======================== 140 passed, 6 xfailed in 2.37s ========================
```

## 3. カバレッジ

○ report-implementer.md の数字と一致した。

```
$ uv run pytest --cov=ytsched --cov-report=term-missing
Name                          Stmts   Miss  Cover
src/ytsched/__init__.py          13      3    77%
src/ytsched/__main__.py          61     61     0%
src/ytsched/edit_handler.py      38      2    95%
src/ytsched/handler.py           70      0   100%
src/ytsched/main_handler.py     300     25    92%
src/ytsched/my_logger.py         26      5    81%
src/ytsched/webapp.py            49      9    82%
src/ytsched/ytsched.py          293      9    97%
TOTAL                           850    114    87%
```

全体87%、handler 100%、ytsched 97%、main_handler 92%、edit_handler 95%、
webapp 82%、`__main__` 0% — すべて report-implementer.md の記載と一致。

## 4. `--runxfail`

○ 6 件がすべて狙った理由で落ちることを確認した。

```
$ uv run pytest --runxfail
======================== 6 failed, 140 passed in 2.36s =========================
```

| テスト | 実際の失敗内容 |
| --- | --- |
| test_load_conf_line_without_tab | ValueError: not enough values to unpack (expected 2, got 1)（handler.py:82） |
| test_import_prints_nothing | AssertionError: 'DAYS_YEAR=365.25, DAYS_MONTH=30.4375\n' == '' |
| test_autoreload_is_not_forced | AssertionError: assert not True（autoreload が True） |
| test_set_time | TypeError: not all arguments converted during string formatting（ytsched.py:320） |
| test_sde_init_date_default_is_not_fixed | AssertionError: assert not True（既定値が datetime.date） |
| test_get_sdf_cache_miss_is_not_warning | AssertionError: Expected 'warning' to not have been called. Called 1 times. |

report-implementer.md の表（TypeError、ValueError、DAYS_YEAR=... の出力、
autoreload=True、既定値が datetime.date、warning の呼び出し）と1件ずつ
対応していることを確認した。

## 5. `~/ytsched` に触れていないか

○ 触れていない。テスト実行前・実行後（2回流した後）とも
`/home/ytani/ytsched` は存在しないまま
（"No such file or directory"）。

## 6. 実行順・再実行での安定性

○ 2回続けて `uv run pytest` を流し、どちらも
**140 passed, 6 xfailed**（同じ内訳）だった。xfail が xpass に化ける、
件数が変わるといった状態の持ち越しは見られなかった。

## 7. アプリの起動確認

○ 起動し、`GET /ytsched/` が 200 を返した。テンプレートは展開されて
いた（応答本文に `{{` / `{%` の生残りは 0 件）。ログに例外・トレース
バックは無く、出ていたのは `WARNING ... cache miss: ...` のみ
（既知の正常系の挙動）。

```
$ uv run ytsched webapp --datadir <tmp> --port 10185
21:41:38 INFO webapp.py.WebServer.main:126> start server: run forever ..
21:41:41 WARNING ytsched.py.SchedData.get_sdf:628> cache miss: date=None
（以下 cache miss の WARNING が続く。例外・トレースバックなし）

$ curl -s -o resp.html -w "HTTP %{http_code}\n" http://127.0.0.1:10185/ytsched/
HTTP 200
$ grep -c "{{" resp.html   # => 0
$ grep -c "{%" resp.html   # => 0
```

補足: 確認後にプロセスを止めようとしたところ、`kill` の前にすでに
プロセスが終了していた（`pgrep` で見つからず）。`run_in_background` の
プロセスが本ツールのシェルセッションの区切りで巻き込まれて終了した
とみられ、`uv run ytsched webapp` 自体の不具合ではない。実データ用の
`--datadir` は指定しておらず、`~/ytsched` は汚していない。

## 結論

依頼された1〜7の項目はすべて○。report-implementer.md の記載と実測が
すべて一致し、新たな不具合は見つからなかった。

## 手直し後の再確認

reviewer 指摘への対応（A〜E）を受けた `tests/` の手直し後に再確認した。
`src/ytsched/` は今回も未変更。

### 1. `uv run pytest`

○ **140 passed, 6 xfailed**（テスト項目は 146 件、report-implementer.md
の追記と一致）。

```
$ uv run pytest
tests/test_handler.py ......xx...x                               [  8%]
tests/test_web.py ...............................                [ 29%]
tests/test_webapp.py ....x                                       [ 32%]
tests/test_ytsched.py ..................................         [ 67%]
...................x...........................x                 [100%]
======================== 140 passed, 6 xfailed in 2.38s ========================
```

（D で `Conf.cgi` 関係の xfail が 1 件増え、A で `set_time` 関係の xfail が
1 件減ったため、`test_handler.py` の x の位置が前回と変わっている。件数は
6 のまま。）

### 2. `--runxfail`

○ **6 failed, 140 passed**。落ちたテストと理由:

| テスト | 実際の失敗内容 |
| --- | --- |
| `test_load_conf_empty_line` | `ValueError: not enough values to unpack (expected 2, got 1)` |
| `test_load_conf_line_without_tab` | 同上（空行の分とタブ無し行の分、2件） |
| `test_import_prints_nothing` | `AssertionError: 'DAYS_YEAR=365.25, DAYS_MONTH=30.4375\n' == ''` |
| `test_autoreload_is_not_forced` | `AssertionError: assert not True`（`autoreload` が `True`） |
| `test_sde_init_date_default_is_not_fixed` | `AssertionError: assert not True`（既定値が `datetime.date`） |
| `test_get_sdf_cache_miss_is_not_warning` | `AssertionError: Expected 'warning' to not have been called. Called 1 times.` |

依頼にあった「`ValueError` ×2（空行・タブ無し行）、`DAYS_YEAR=...` の出力、
`autoreload=True`、既定値が `datetime.date`、`warning` の呼び出し」の
6 つに 1 対 1 で対応していることを確認した。`test_set_time` 関係の
xfail は無くなっている（A の対応どおり、xfail を廃止して通常のテストに
なった）。

### 3. カバレッジ

○ **全体 87% のまま変化なし**。`handler.py` 100%、`ytsched.py` 97%、
`main_handler.py` 92%、`edit_handler.py` 95%、`webapp.py` 82%、
`__main__.py` 0% も前回と同じ。

### 4. B の直しの再現確認（自分で壊してみた）

`src/ytsched/` は書き換えず、`main_handler` モジュール内だけで
`re.search()` をラッパーに差し替える pytest プラグインを作業用
ディレクトリに置き、`-p` でロードして確かめた
（`/tmp/.../scratchpad/break_plugin.py`、`PYTHONPATH` 経由で読み込み）。

- **絞り込みが全件を消す壊れ方**（`re.search()` が常に不一致を返す）
  → `tests/test_web.py -k "filter_str or search_str"` で
  **5 failed, 2 passed**。落ちたのは
  `test_filter_str` / `test_filter_str_negative` /
  `test_saved_filter_str_is_reused` / `test_search_str` /
  `test_todo_with_search_str`
- **絞り込みが何も除外しない壊れ方**（`re.search()` が常に一致を返す）
  → 同じく **5 failed, 2 passed**。落ちたのは
  `test_filter_str` / `test_filter_str_negative` /
  `test_saved_filter_str_is_reused` / `test_search_str` /
  `test_todo_with_filter_str`

**両方向の壊れ方で `test_filter_str` と `test_search_str` の両方が
落ちる**ことを確認した。B の直しは効いている。

（実装の手段は implementer の
「`SchedDataEnt.search_str()` を差し替える」とは異なり、こちらは
`main_handler` モジュール内だけで `re.search()` を差し替える方法を
取った。どちらも「絞り込みが常に不一致 / 常に一致になる」という
壊れ方を作る点は同じで、結果として `test_filter_str` /
`test_search_str` が両方向で落ちることを別の壊し方でも再現できた。）

### 5. `~/ytsched`

○ 検証作業（プラグインを使った実行を含む）の前後とも
`/home/ytani/ytsched` は存在しないまま。

### 6. 再実行での安定性

○ 手直し後のテストも 2 回続けて流し、どちらも
**140 passed, 6 xfailed**（同じ内訳）だった。

### 結論（手直し後）

依頼された 1〜6 の項目はすべて○。A〜E の対応は report-implementer.md の
記載どおりで、B の直しも自分で壊し方を作って再現・確認できた。新たな
不具合は見つからなかった。
