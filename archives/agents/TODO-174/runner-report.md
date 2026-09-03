# 実行結果レポート（TODO-174）

## 1. pytest

コマンド:
```
uv run pytest tests/test_web.py -q
```

結果: 成功（終了ステータス 0）

出力:
```
........................................................................ [ 45%]
........................................................................ [ 91%]
..............                                                           [100%]
158 passed in 5.55s
```

---

## 2. ruff format (check)

コマンド:
```
uv run ruff format --check tests/test_web.py
```

結果: 成功（終了ステータス 0）

出力: `1 file already formatted`

---

## 3. ruff check

コマンド:
```
uv run ruff check tests/test_web.py
```

結果: 成功（終了ステータス 0）

出力: `All checks passed!`

---

## 概要

すべてのコマンドが成功しました。テストは 158 件が pass し、lint・format ともエラーなし。
