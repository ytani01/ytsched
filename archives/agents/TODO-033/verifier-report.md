# TODO-033 verifier 報告

## 1. 静的解析・テスト

すべて `implementer-report.md` の内容と一致した。

```
$ uv run ruff format --check --line-length 78 src tests
unformatted: File would be reformatted
   --> src/ytsched/__main__.py:198:12
    |
197 | )
    - def webapp(port, webroot, datadir, urlprefix, days, size_limit, version, debug):
198 + def webapp(
199 +     port, webroot, datadir, urlprefix, days, size_limit, version, debug
200 + ):
201 |     """webapp"""
--------------------------------------------------------------------------------
205 |     app = WebServer(
    -         port, webroot, datadir, urlprefix, days, size_limit, version, debug=debug
206 +         port,
...
1 file would be reformatted, 20 files already formatted

$ uv run ruff check --extend-select I src tests
All checks passed!

$ uv run basedpyright src tests
0 errors, 0 warnings, 0 notes

$ uv run mypy src tests
Success: no issues found in 18 source files

$ uv run pytest tests
collected 380 items
tests/test_handler.py ...............                                    [  3%]
tests/test_main_handler.py .......................................       [ 14%]
tests/test_migrate.py .................................................. [ 27%]
...............                                                          [ 31%]
tests/test_mylog.py ........                                             [ 33%]
tests/test_web.py ...................................................... [ 47%]
........................................                                 [ 58%]
tests/test_webapp.py ......                                              [ 59%]
tests/test_ytsched.py .................................................. [ 72%]
........................................................................ [ 91%]
...............................                                          [100%]
380 passed in 1.37s
```

collect も止まらず、全件通った。〇

## 2. `URL_PREFIX` の残存確認

`git grep -n URL_PREFIX` の結果、`src/ytsched/` 配下は `webapp.py` の
`DEF_URL_PREFIX`（定義）と `__main__.py` の `WebServer.DEF_URL_PREFIX`
（参照）のみ。テスト側は `tests/helpers.py:23` が
`URL_PREFIX = WebServer.DEF_URL_PREFIX` に、`tests/test_webapp.py:30,34`
も `WebServer.DEF_URL_PREFIX` になっている。それ以外の `URL_PREFIX` は
すべて `tests/helpers.py` の**モジュール変数** `URL_PREFIX` を import
して使っているもので、依頼どおり残してよいもの。`WebServer.URL_PREFIX`
という参照は 1 つも残っていなかった。〇

`archives/` 配下・`TODO.md` に出てくる `URL_PREFIX` は過去の項目
（TODO-003・TODO-015・TODO-021）の記録や、今回の TODO-033 自体の背景
説明なので無関係。

## 3. `src/README.md` の記述

`src/README.md:70`

```
組み立てる。URL は既定で `/ytsched`（`WebServer.DEF_URL_PREFIX`）配下。
```

実物と照合。

- `src/ytsched/webapp.py:34` — `DEF_URL_PREFIX = "/ytsched"`。
  既定値 `/ytsched` は合っている
- `src/ytsched/webapp.py:51` — `url_prefix: str = DEF_URL_PREFIX` を
  `WebServer.__init__()` が受け取る
- `src/ytsched/__main__.py:164-170` — CLI オプションは
  `--urlprefix`（`-u`）で、既定値は `WebServer.DEF_URL_PREFIX`。
  実際に変更できることも確認済み（後述 5.）

食い違いなし。〇

**気になった点（判断は main へ）**: `implementer-request.md` /
`implementer-report.md` / この verifier 自身への依頼書はいずれも
CLI オプション名を `--url-prefix`（ハイフン入り）と書いているが、
`__main__.py:165` の実際のオプション名は `--urlprefix`
（ハイフンなし）。`src/README.md` はオプション名そのものを書いて
いない（実装者が「1 行に収まらないので名前は書かない」と判断した
とおり）ので、README と実物の食い違いにはなっていない。依頼書側の
表記が実物と違っていただけで、コードや README には影響しない。

## 4. `src/ytsched/__main__.py` を直さなかった判断について

実装者の見立て（`2b4fcce feat(webapp): add url_prefix option` で
入った `webapp()` の引数列・`WebServer(...)` の呼び出しが 78 桁を
超えているだけで、TODO-033 の変更（`URL_PREFIX` → `DEF_URL_PREFIX`
への追随）とは無関係）は、`git blame` や diff の内容と整合していた。
実際に `ruff format --check` で崩れているのはこの 2 か所のみで、
TODO-033 の変更対象（`tests/helpers.py` / `tests/test_webapp.py` /
`src/README.md`）とは別ファイル・別理由。**範囲外という見立ては妥当**
と判断する。直すかどうか（このコミットに混ぜる／別項目にする）は
main の判断でよい。

## 5. アプリの起動確認

`--datadir` はいずれも一時ディレクトリ、ポートは 8892 を使用。

```
$ uv run ytsched webapp --port 8892 \
    --datadir <tmp1> \
  （既定の url_prefix のまま）
$ curl -s -o /dev/null -w '%{http_code}' http://localhost:8892/ytsched/
200
$ curl -s -o /dev/null -w '%{http_code}' http://localhost:8892/ytsched
200
```

ログに例外・トレースバックなし（`start server: run forever ..` のみ）。

```
$ uv run ytsched webapp --port 8892 --urlprefix /custom \
    --datadir <tmp2>
$ curl -s -o /dev/null -w '%{http_code}' http://localhost:8892/custom/
200
$ curl -s -o /dev/null -w '%{http_code}' http://localhost:8892/ytsched/
404   # 既定の /ytsched/ には来なくなっている（想定どおり）
```

ログには `404 GET /ytsched/ (::1) ...` の 1 行のみで、例外はなし。

`/custom/` の HTML を取得して `grep -c '{{'` / `grep -c '{%'` を実行、
どちらも 0 件で、テンプレートが生のまま残っていないことも確認した。

両方のプロセスとも `pgrep -f` で PID を確認してから `kill` し、
`--datadir` に渡した一時ディレクトリ以外（`~/ytsched/data`）には
一切触れていない。

## 総合判断

依頼書の 5 項目すべて確認でき、不具合は見つからなかった。〇
