# TODO-100 verifier 報告

## 確認したこと（すべて○）

1. データファイルのパスが今までと同じか
   - `date2path()` の新旧実装を Python で実際に呼び比べ、同じ `topdir`・
     `date` から同じ文字列（`/home/x/ytsched/data/2026/01/05.jsonl`、
     `ToDo.jsonl`）が出ることを確認した（桁揃え、年・月ディレクトリ、
     拡張子とも一致）

2. `.bak` の名前
   - `pathname_old + BACKUP_EXT` と
     `Path(pathname_old).with_name(p.name + BACKUP_EXT)` を実際に計算し、
     一致することを確認（`/home/x/data/2026/01/05.jsonl.bak`）

3. `~` の展開
   - `~`、`~/foo`、`/abs/path` は `os.path.expanduser` と
     `Path(...).expanduser()` で結果が一致
   - **差異を 2 件見つけた（実装への波及は無いと判断したが記録する）**
     - 空文字列 `""`: 旧 `os.path.expanduser("")` → `""`、新
       `Path("").expanduser()` → `"."`。ただし `DEF_TOP_DIR`/`DEF_DATADIR`
       のデフォルト値・CLI のデフォルト値のいずれも空文字ではないため、
       現状のコードパスでは到達しない
     - `~user_nonexistent/x`（存在しないユーザ名）: 旧は展開できず文字列を
       そのまま返す（黙って無視）、新は `RuntimeError: Could not determine
       home directory.` を送出する。存在しないログイン名を渡す経路は
       通常の利用では無い

4. `os.path.abspath` → `.absolute()`
   - `webapp.py:39`: `DEF_WEBROOT = Path(__file__).absolute().parent /
     "webroot"`。実際にアプリを起動し static/template が読めていることを
     確認（後述）

5. CLI からの `str` 経路
   - `uv run ytsched webapp --datadir <一時ディレクトリ>` を起動し、
     `curl http://127.0.0.1:18765/ytsched/` → **200**。ログに例外・
     トレースバックなし
   - `uv run ytsched migrate --datadir <一時ディレクトリ> --dry-run` を
     実行し、正常終了（変換 0 件、警告ログのみで例外なし）

6. `uv run ruff check .` → All checks passed
   `uv run mypy src` → Success: no issues found in 14 source files
   `uv run basedpyright` → 0 errors, 0 warnings, 0 notes
   `uv run pytest tests -q --ignore=tests/test_browser.py` → 459 passed
   （`test_browser.py` は重いため省略。implementer 報告で確認済み）

7. `os.path`/`os.stat`/`os.makedirs`/生の `open()` の残骸
   - `grep` では見つからず。`docstring` 中の「``os.stat()`` は 1 回だけ
     呼ぶ」等の記述のみ残っているが、これは implementer 報告の「気づいたが
     直していないこと」に既に書かれている既知の件
   - `pathname + ...`／`%` 書式／`.startswith(pathname)` のような、Path
     属性を str として扱っている箇所は見つからなかった
     （`.startswith` の 3 箇所はいずれも str 属性で無関係）

## 不具合

無し。ただし 3 の差異（空文字列・存在しないユーザ名）は判断材料として記録した。
到達経路が無いため、対応するかどうかは main の判断に委ねる。
