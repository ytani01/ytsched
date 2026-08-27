# runner 報告 — TODO-083 コメント修正後の再確認

## `mise run lint`

終了ステータス: 0（○）

```
# ruff format
28 files left unchanged
# ruff check
All checks passed!
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 25 source files
```

## `mise run typecheck`

終了ステータス: 0（○）

```
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 25 source files
```

## `mise run test`

終了ステータス: 0（○）

```
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/ytani/work/ytsched
configfile: pyproject.toml
plugins: cov-7.1.0
collected 475 items

tests/test_browser.py ...................                                [  4%]
tests/test_handler.py ..............                                     [  6%]
tests/test_handler_util.py ..........                                    [  9%]
tests/test_main_handler.py ............................................. [ 18%]
........                                                                 [ 20%]
tests/test_migrate.py .................................................. [ 30%]
.......................                                                  [ 35%]
tests/test_mylog.py ........                                             [ 37%]
tests/test_web.py ...................................................... [ 48%]
......................................................................   [ 63%]
tests/test_webapp.py ........                                            [ 65%]
tests/test_ytsched.py .................................................. [ 75%]
........................................................................ [ 90%]
............................................                             [100%]

============================= 475 passed in 55.99s =============================
```

## 確認事項

- `test_browser.py` は 19 件が `...................` のすべて pass（skip されていない）
- 全体で 475 件が passed（新たなエラー・警告なし）
