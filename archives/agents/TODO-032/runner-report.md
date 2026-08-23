# TODO-032 runner report

## 1. uv run ruff format --line-length 78 --check src tests tools

終了ステータス: 0（○）
出力: 22 files already formatted

## 2. uv run ruff check --extend-select I src tests tools

終了ステータス: 0（○）
出力: All checks passed!

## 3. uv run basedpyright src tests tools

終了ステータス: 0（○）
出力: 0 errors, 0 warnings, 0 notes

## 4. uv run mypy src tests

終了ステータス: 0（○）
出力: Success: no issues found in 18 source files

## 5. uv run pytest tests

終了ステータス: 0（○）
出力: 412 passed in 2.94s

---

## まとめ

すべてのコマンドが成功。ファイルの書き換えなし。
