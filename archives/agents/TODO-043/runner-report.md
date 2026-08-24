# runner-report — TODO-043

## mise run lint

終了ステータス: 0 ✓

```
# ruff format
23 files left unchanged
# ruff check
All checks passed!
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 20 source files
```

Finished in 5.43s

## mise run test

終了ステータス: 0 ✓

```
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/ytani/work/ytsched
configfile: pyproject.toml
plugins: cov-7.1.0
collected 418 items

tests/test_handler.py .................                                  [  4%]
tests/test_main_handler.py ............................................. [ 14%]
....                                                                     [ 15%]
tests/test_migrate.py .................................................. [ 27%]
.......................                                                  [ 33%]
tests/test_mylog.py ........                                             [ 35%]
tests/test_web.py ...................................................... [ 48%]
..................................................                       [ 60%]
tests/test_webapp.py ........                                             [ 61%]
tests/test_ytsched.py .................................................. [ 73%]
........................................................................ [ 91%]
.....................................                                    [100%]

============================= 418 passed in 2.64s ==============================
```

Finished in 8.73s
