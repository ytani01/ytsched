# runner-report（TODO-021 最終確認）

## コマンド実行結果

### 1. uv run ruff format --line-length 78 src tests
- 終了ステータス: 0 ○
- 出力: `19 files left unchanged`

### 2. uv run ruff check --fix --extend-select I src tests
- 終了ステータス: 0 ○
- 出力: `All checks passed!`

### 3. uv run basedpyright src tests
- 終了ステータス: 0 ○
- 出力: `0 errors, 0 warnings, 0 notes`

### 4. uv run mypy src tests
- 終了ステータス: 0 ○
- 出力: `Success: no issues found in 18 source files`

### 5. uv run pytest tests
- 終了ステータス: 0 ○
- 出力: `330 passed in 1.34s`（期待値 330 passed）

## ruff による書き換え
無し。ruff format・check で変更されたファイルはなし。

## まとめ
すべてのコマンドが成功。pytest は期待値の 330 passed を達成。
