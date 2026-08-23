# TODO-035 runner 報告

## 1. mise run lint

終了ステータス: 0（○）

```
[fmt] $ echo "# ruff format"
# ruff format
22 files left unchanged
# ruff check
All checks passed!
[typecheck] $ echo "# basedpyright"
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 19 source files
Finished in 5.38s
```

## 2. uv run pytest tests

終了ステータス: 0（○）

```
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/ytani/work/ytsched
configfile: pyproject.toml
plugins: cov-7.1.0
collected 404 items

tests/test_handler.py ...............                                    [  3%]
tests/test_main_handler.py ............................................. [ 14%]
....                                                                     [ 15%]
tests/test_migrate.py .................................................. [ 28%]
.................                                                        [ 32%]
tests/test_mylog.py ........                                             [ 34%]
tests/test_web.py ...................................................... [ 47%]
..............................................                           [ 59%]
tests/test_webapp.py ......                                              [ 60%]
tests/test_ytsched.py .................................................. [ 73%]
........................................................................ [ 90%]
.....................................                                    [100%]

============================= 404 passed in 2.91s ==============================
```

## 3. uv run python tools/token-usage.py --list

終了ステータス: 0（○）

TODO-013 と TODO-022 の行：

```
TODO-013   2026-08-19 21:20:55  2026-08-19 21:21:09 
TODO-022   2026-08-21 04:36:44  2026-08-21 04:43:51 
```

注：修正前は「(未完了)」と表示されていたが、修正により終点の時刻が表示されるようになった。`show_list()` のバグが直ったことを確認。

## 4. uv run python tools/token-usage.py TODO-034

終了ステータス: 0（○）

```
消費: output 21,282 / cache_creation 163,913
```

期待値と一致。

## 5. uv run python tools/token-usage.py TODO-029

終了ステータス: 0（○）

```
消費: output 47,356 / cache_creation 1,042,774
```

期待値と一致。
