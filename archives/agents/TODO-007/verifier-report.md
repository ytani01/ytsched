# TODO-007 verifier 報告

実装者の報告（`implementer-report.md`）を読んだうえで、依頼の項目を
すべて自分で実行し直して確かめた。**実装者の報告の数値・挙動は
すべて再現できた。** 見つけた不具合は無い（ただし依頼の想定外の
1 点だけ、追加確認が要ったので下に書く）。

## 1. `uv run pytest`

```
$ uv run pytest -q
169 passed in 0.93s
```

依頼どおり 169 passed。`test_mylog.py` を単独でも実行し、8 件すべて
PASSED。

## 2. `uv run mypy src tests`

```
$ uv run mypy src tests
Success: no issues found in 14 source files
```

エラー 0。実装者の報告どおり。

## 3. `uv run basedpyright src tests`

```
$ uv run basedpyright src tests
0 errors, 0 warnings, 0 notes
```

エラー 0。実装者の報告どおり。

## 4. `uv run ruff check src tests`

着手後（現状）:

```
Found 86 errors.
```

内訳（`--output-format=concise` から規則ごとに集計）:

```
34 UP031
13 FLY002
13 DTZ011
10 D419
 5 RUF012
 4 EXE001
 2 SIM102
 1 SIM118
 1 PLC0206
 1 PERF402
 1 DTZ005
 1 C408
```

`git stash -u` で実装前の状態に戻し、同じコマンドで確認（着手前）:

```
Found 87 errors.
```

内訳:

```
35 UP031
13 FLY002
13 DTZ011
10 D419
 5 RUF012
 4 EXE001
 2 SIM102
 1 SIM118
 1 PLC0206
 1 PERF402
 1 DTZ005
 1 C408
```

**着手前 87 件・着手後 86 件、規則ごとの内訳も実装者の報告の表と完全に
一致した。増えた規則は無い**（UP031 が 35→34 に 1 件減っただけ）。
確認後 `git stash pop` で戻し、`git status` で元の状態
（未追跡ファイル・変更ファイルの一覧）に復元されたことと、
`uv run pytest` が 169 passed のままであることを確認した。

（補足）stash pop 後、`src/ytsched/my_logger.py` の削除が「ステージ
済み」から「未ステージ」に変わった（`git status` の表示上の違いのみ）。
削除自体は変わらず、内容の欠落は無い。コミットするときの `git add`
対象に影響するので、念のため書いておく。

## 5. `uv run ruff format --check src tests`

依頼どおりのコマンド（`--line-length` 指定なし、既定 88 桁）では：

```
$ uv run ruff format --check src tests
9 files would be reformatted, 5 files already formatted
```

**通らない。** ただし `mise.toml` の `lint` タスクは
`ruff format --line-length 78 src tests` を使っており、プロジェクトの
規約（行長 78）はそちらに合わせて `--line-length 78` を明示的に渡す
前提になっている。実際にそちらで確認すると：

```
$ uv run ruff format --line-length 78 --check src tests
14 files already formatted
```

**通る。** 実装者の報告の「14 files already formatted」はこの
`--line-length 78` の結果であり、一致した。
`pyproject.toml` に `[tool.ruff]` の `line-length` 設定は無く、
`mise.toml` の `lint` タスク側だけに `--line-length 78` が
ハードコードされている状態。依頼文の「`ruff format --check`」を
そのまま実行すると失敗するが、これは TODO-007 の変更が原因ではなく
（着手前から `--line-length` を指定しないと同じ状況になるはず）、
プロジェクトの ruff format 実行手順（`--line-length` を明示しないと
コマンド名だけでは通らない）についての既存の構成の話。
**main の判断が要る点として報告する**（`pyproject.toml` に
`line-length = 78` を足すかどうかは TODO-007 の範囲外と思われる）。

## 6. `my_logger.py` への参照

```
$ grep -rn "my_logger\|get_logger\|_mylog\|_dbg" src tests
src/ytsched/webapp.py:74:        self._dbg = debug
src/ytsched/webapp.py:104:            autoreload=self._dbg,
src/ytsched/webapp.py:112:            debug=self._dbg,
```

想定どおり `webapp.py` の `self._dbg`（tornado 用）だけが残っている。
`my_logger` / `get_logger` / `_mylog` への参照は 0 件。

## 7. 実際に動かした

`--datadir` は毎回 `/tmp/tmp.R8F7dPbowb/...` 配下の一時ディレクトリを
使った。`~/ytsched/data` には触れていない。

### 7-1. help

`uv run ytsched --help` / `uv run ytsched webapp --help` は従来どおりの
表示。`-d, --debug  debug flag` も残っている。

### 7-2. `--debug` 無しで起動

```
$ uv run ytsched webapp --port 18085 --datadir <tmp>/nodebug
08/20 09:54:22 ℹ️ INFO webapp.py:126 main()> start server: run forever ..
$ curl -s -o /dev/null -w "HTTP:%{http_code}\n" http://127.0.0.1:18085/ytsched/
HTTP:200
```

ログは INFO の 1 行だけ。`GET /ytsched/` は 200。実装者の報告と一致。
kill 後 `pgrep` で残プロセスが無いことを確認。

### 7-3. `--debug` 付きで起動

```
$ curl -s -o /dev/null -w "HTTP:%{http_code}\n" http://127.0.0.1:18086/ytsched/
HTTP:200
```

DEBUG ログの形式は `🐞 DEBUG ファイル名:行 関数()> メッセージ`。
取得した HTML も `<!DOCTYPE HTML>` から始まり正しく展開されていて、
`{{ }}` や `{%` の生残りは無い。

行番号の実物照合（数か所を抜き取り）:

- `ytsched.py:417 load()> ...: not found .. ignored`
  → `src/ytsched/ytsched.py:417` は
  `self.__log.debug(f"{self.pathname}: not found .. ignored")` で一致
- `handler.py:38 __init__()> app=...` / `handler.py:39 __init__()>
  req=...`
  → `src/ytsched/handler.py:38-39` は
  `self.__log.debug(f"app={app}")` / `self.__log.debug(f"req={req}")`
  で一致
- `main_handler.py:107 get()> request=...` / `main_handler.py:108
  get()> request.path=...`
  → `src/ytsched/main_handler.py:107-108` と一致
- `edit_handler.py:47 get()> date=None, sde_id=None, todo_flag=False`
  → `src/ytsched/edit_handler.py:47` は複数行にまたがる
  `self.__log.debug(\n    f"date={date}, ..."\n)` の開始行で一致
  （loguru の `depth` は正しく呼び出し元を指している）

いずれも `mylog.py` の行ではなく、呼び出し元の実物の行番号・関数名が
出ている。

### 7-4. `POST cmd=add`

最初、`date=2026/08/20`（スラッシュ区切り）で送ると
`ValueError: Invalid isoformat string: '2026/08/20'` で 500 になった。
実装は `datetime.date.fromisoformat()` を使っており、フォームからの
`date` は ISO 形式（`YYYY-MM-DD`）を期待している。これは TODO-007 の
変更点ではなく、既存の仕様（依頼メモの想定と実際のフォーム形式が
違っていただけ）。`date=2026-08-20` に直すと `400 Missing argument
sde_id` になった（`add` でも `sde_id` パラメータが必須で、空文字
`sde_id=` を渡す必要がある）。これも既存の仕様で、TODO-016
（`sde_id` が無いと 400 になる件）と符合する。

`sde_id=` を足して再送すると 200 になり、データファイルが
タブ区切りで正しく書かれた:

```
$ cat <tmp>/debug/2026/08/20.cgi
bfec42d8-956a-4d22-a269-fa46eaf3fbba	2026/08/20	09:00-:		verify-test
```

このリクエストのログに WARNING / ERROR は無かった。

### 7-5. `x-data1`

```
$ uv run ytsched x-data1 2026 8 20 --datadir <tmp>/x1
08/20 09:55:55 ℹ️ INFO __main__.py:91 x_data1()> end
===== No data =====

$ uv run ytsched x-data1 2026 8 20 --datadir <tmp>/x1 -d
08/20 09:55:55 🐞 DEBUG __main__.py:25 __init__()> yyyy/mm/dd=2026/8/20
...(中略、__main__.py と ytsched.py の DEBUG が出る)...
08/20 09:55:55 ℹ️ INFO __main__.py:91 x_data1()> end
===== No data =====
```

`-d` 無しでは INFO 1 行、付きでは `__main__.py` / `ytsched.py` の
DEBUG が出た。実装者の報告と一致。

### 7-6. サーバの停止確認

起動した 2 つのサーバ（`--port 18085` / `18086`）はいずれも kill し、
`pgrep -f "ytsched webapp"` で残プロセスが無いことを確認した。

## 8. ログの水準

`--debug` 無しのとき DEBUG は 1 行も混ざらなかった（INFO 1 行のみ）。

`--debug` 付きのとき、全 5 モジュールから DEBUG が出ることを確認:

```
$ grep -oE "DEBUG [a-z_]+\.py" <tmp>/debug.log | sort | uniq -c
     69 DEBUG handler.py
     82 DEBUG main_handler.py
      5 DEBUG webapp.py
    280 DEBUG ytsched.py
```

`edit_handler.py` は `GET /ytsched/edit` を叩くまで 0 件だった
（メインページの GET/POST だけでは経由しないので当然）。
`curl "http://127.0.0.1:18086/ytsched/edit?date=2026-08-20&sde_id=..."`
を叩くと `edit_handler.py` からも 5 件の DEBUG が出た。
5 モジュールすべてから DEBUG が出ることを確認できた。

## 9. `tests/test_mylog.py` / `mylog.py` の実物照合

```
$ diff ~/work/tmr/tests/test_mylog.py tests/test_mylog.py
```

差分は先頭の著作権表示 3 行と、import 先（`tmr` → `ytsched`）だけ。
テストの中身（8 件）は変えていない。

```
$ diff ~/work/tmr/src/tmr/mylog.py src/ytsched/mylog.py
```

差分は docstring 中のサンプルコード（クラス名を `SchedDataEnt` /
`HandlerBase` / `MainHandler` に書き換えた部分）のみ。`getLogger` /
`setLevel` / `loggerInit` / `logLevel` / `_filter` / `exmsg` /
`LOG_FMT` の実装は 1 文字も変わっていない。`~/work/tmr` 側は読むのみで
書き換えていない。

## まとめ

依頼の 1〜9 すべてを自分で実行し、実装者の報告の数値・挙動と
完全に一致することを確認した。コードの不具合は見つからなかった。

**main の判断が要る点は 1 つだけ**（項目 5）。依頼文どおり
`uv run ruff format --check src tests` を素のまま実行すると
`9 files would be reformatted` になる。プロジェクトの規約は行長 78 で、
`mise.toml` の `lint` タスクは `--line-length 78` を明示的に渡している
（`pyproject.toml` に `[tool.ruff] line-length` の設定が無い）。
`--line-length 78` を付ければ実装者の報告どおり
`14 files already formatted` で通る。TODO-007 の変更が原因ではなく
既存の構成によるものだが、依頼の書き方と実際のコマンドが食い違って
いたので報告する。
