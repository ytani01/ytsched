# TODO-030 verifier 報告

writer の報告は読まず、実際にコマンドを叩いて確かめた。文書は直していない。

## 1. コマンド例が書いたとおりに動くか

```sh
$ mise tasks
build           build
fmt             format (ruff)
lint            linting (fmt, typecheck)
test            test
typecheck       type check (basedpyright, mypy)
webapp          run web server
migrate         migrate old data (.cgi) to JSON Lines
upgradeproject  upgrade in this project
...
```

`mise.toml` を読むと、依存関係は `build` → `test` → `lint` → (`fmt`,
`typecheck`) の順。`docs/Developer.md` の記述（「`build` は `test` に、
`test` は `lint` に、`lint` は `fmt` と `typecheck` の両方に依存する」）と
一致。○

```sh
$ mise run lint
[fmt] $ echo "# ruff format" / # ruff format / 21 files left unchanged
# ruff check / All checks passed!
[typecheck] $ echo "# basedpyright" / # basedpyright / 0 errors, 0 warnings, 0 notes
# mypy / Success: no issues found in 18 source files
```
○ 通った。

```sh
$ uv run pytest tests
============================= 330 passed in 1.19s ==============================
```
○ 330 件すべて通過。

```sh
$ uv run ytsched migrate --help
Usage: ytsched migrate [OPTIONS]
  旧形式(タブ区切り .cgi)のデータを JSON Lines (.jsonl) へ変換する
  元の .cgi は消さない。既に .jsonl があるファイルは飛ばす。
Options:
  --datadir, --data PATH  data directory, default='~/ytsched/data'
  --dry-run               書き出さずに、件数だけ出す
  --error-file PATH       変換できなかった行の書き出し先, default='migrate-errors.txt'
  -d, --debug             debug flag
  -h, --help              Show this message and exit.
```
`docs/Developer.md` の「オプションは data-format.md 参照」の指示どおり、
`data-format.md` に `--dry-run` 等の記述があるか確認。○（`--datadir` の
既定 `~/ytsched/data` も一致）。実データには触れていない。

```sh
$ uv run ytsched webapp --help
Options:
  -p, --port INTEGER        port number, default=10085
  -w, --datadir PATH        data directory, default='/home/ytani/ytsched/data'
  ...
```
README.md の systemd ユニット（`ExecStart=%h/.local/bin/ytsched webapp
--datadir %h/ytsched/data --port 10085`）のオプション名・既定値と一致。○

**アプリの起動確認**（`--datadir` は一時ディレクトリ）:

```sh
$ mkdir -p <scratchpad>/verify-datadir
$ uv run ytsched webapp --datadir <scratchpad>/verify-datadir --port 18099 &
$ curl -s -o out.html -w "%{http_code}\n" http://127.0.0.1:18099/ytsched/
200
```
ログ（`webapp.log`）に例外・トレースバックなし。取得した HTML に
`{{` `{%` の生残りは 0 件（`grep -c` で確認）。プロセスは `pgrep -af` で
PID を確認してから `kill` し、停止を確認した。○

`mise run upgradeproject` は走らせていない。

## 2. src/README.md・tests/README.md が実物と合っているか

```sh
$ ls src/ytsched/
__init__.py  __main__.py  edit_handler.py  handler.py  main_handler.py
migrate.py   mylog.py     webapp.py        webroot      ytsched.py
$ ls tests/
data  helpers.py  make_test_data.py  README.md  test_handler.py
test_main_handler.py  test_migrate.py  test_mylog.py  test_web.py
test_webapp.py  test_ytsched.py
```

`src/README.md` のモジュール一覧・`tests/README.md` のファイル一覧とも、
実物と一致。○（`test_main_handler.py`・`test_migrate.py` を含む 7 本の
テストファイルすべて記載あり）

`COOKIE_TODO_DAYS` は `src/ytsched/main_handler.py:96` に実在し、
`src/README.md` はこの語を使っていない（該当しない懸念）。

テストの件数（330 件）は `src/README.md`・`tests/README.md` のどちらにも
明記されていないので、実測とのズレは無い（そもそも書いていない）。

## 3. リンク・画像が辿れるか

6 文書すべての Markdown リンクを機械的に解決した（相対パスを文書の
ディレクトリから展開）。

```
README.md            : docs/fig1.png OK / docs/Developer.md OK / docs/data-format.md OK
docs/Developer.md     : ../README.md OK / ../src/README.md OK / ../tests/README.md OK
                        (x2) / data-format.md OK (x2) / javascript-scroll.svg OK
docs/data-format.md   : ../src/README.md OK / Developer.md OK / ../tests/README.md OK
                        / ../README.md OK
src/README.md         : ../README.md OK / ../docs/Developer.md OK
                        / ../tests/README.md OK / ../docs/data-format.md OK
tests/README.md       : ../docs/Developer.md OK / ../src/README.md OK
CLAUDE.md             : （Markdown リンクなし）
```
すべて辿れた。○ `README.md` から移した `javascript-scroll.svg` の参照は
`docs/Developer.md` 内で `![](javascript-scroll.svg)`（同じ `docs/` 内、
拡張子なし相対パス）になっており、実在ファイル `docs/javascript-scroll.svg`
と一致。○

`docs/` には `sample1.png` `refill1.jpg` もあるが、これは今回の変更前
（`git show HEAD:README.md`）から一度も参照されていない画像で、今回の
移動漏れではない（参考情報として報告）。

## 4. 移し漏れ

`git diff CLAUDE.md` で削られた記述を 1 つずつ、新しい 6 文書に当たった。
ほとんどは `src/README.md` または `docs/data-format.md` に移っているか、
`docs/data-format.md` のほうがむしろ詳しくなっている。**ただし次の 2 点は
どの文書にも見当たらなかった。**

- **`SchedDataFile` のパスの決め方 `date2path()`**（「日付ありなら
  `{topdir}/{年}/{月}/{日}.jsonl`、`date=None` なら ToDo として
  `{topdir}/ToDo.jsonl`」）。`src/README.md` にも `docs/data-format.md`
  にも `date2path` という語自体が無い（`grep -rn "date2path" --include="*.md" .`
  で archives 以外ヒット無し）
- **`detail` の改行表示を CSS の `white-space: pre-wrap` が担っている
  という注記**（「テンプレート側でタグを差し込んでいるわけではない」）。
  `pre-wrap` という語は `TODO.md`（別項目 TODO-093 がらみの文脈）にしか
  無く、6 文書側には無い（`grep -rn "pre-wrap" --include="*.md" .` で
  6 文書には未ヒット）

`README.md` の「memo」節（JavaScript `Date` の罠、
`javascript-scroll.svg`）は両方とも `docs/Developer.md` の「memo」節へ
そのまま移っており、移し漏れは無い。○

## 5. 役割分担

- `docs/Developer.md` に**テストの構成そのもの**（各ファイルの役割等）は
  無く、「走らせ方」（`mise run test` / `pytest` の叩き方、
  `make_test_data.py` の再生成）だけに留まっている。構成は
  `tests/README.md` を参照する形になっている。○
- `src/README.md` に、メソッドごとの引数一覧のような docstring 相当の
  細部は書かれていない（クラス構造とデータフローの説明に留まる）。○
- `docs/data-format.md` は `git diff` で確認したところ、相互リンクの
  4 行を足しただけで、本文の変更は無い。○

## まとめ

- コマンド例（`mise tasks` / `mise run lint` / `pytest` 330 件 / `migrate
  --help` / `webapp --help` / 実起動 HTTP 200・例外無し）はすべて書かれた
  とおりに動いた
- `src/README.md`・`tests/README.md` は実物と一致
- 6 文書のリンク・画像参照はすべて辿れた
- **移し漏れが 2 件見つかった**（`date2path()` のパスの決め方、
  `detail` の改行表示を `white-space: pre-wrap` が担っているという注記）。
  どちらも旧 `CLAUDE.md` にあった記述で、新しい 6 文書のどこにも
  見当たらない。落として構わないかどうかは判断していない（報告のみ）
- 役割分担（`docs/Developer.md` にテスト構成が残っていないか、
  `docs/data-format.md` の中身が変わっていないか）は守られていた
