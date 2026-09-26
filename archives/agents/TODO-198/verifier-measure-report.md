# TODO-198 verifier 実測報告

## 手順

```
git -C ~/work/ytsched worktree add --detach /tmp/.../scratchpad/wt198 HEAD
cd /tmp/.../scratchpad/wt198
cat > tests/test_tmp198.py <<'EOF'
x: int = "a"


def test_ok():
    pass
EOF
mise trust
mise run test
```

（`x: int = "a"` は typecheck だけを落とすつもりで足したファイル。ただし
実際には typecheck に到達する前に fmtjs で止まった。下記参照）

## 結果

終了ステータス: `1`

出力（全文）:

```
[fmtjs] $ npx --no-install prettier --write src/ytsched/webroot/static/js
[fmt] $ echo "# ruff format"
[fmt] # ruff format
[fmt] Using CPython 3.14.7 interpreter at: /usr/bin/python3.14
[fmt] Creating virtual environment at: .venv
[fmtjs] npm error npx canceled due to missing packages and no YES option: ["prettier@3.9.9"]
[fmtjs] npm error A complete log of this run can be found in: /home/ytani/.npm/_logs/2026-09-26T21_20_04_015Z-debug-0.log
Finished in 305.5ms
[fmtjs] ERROR task failed
```

## 見たこと

- **fmtjs が先に失敗した**（prettier が npx でインストールされておらず
  `npm error npx canceled`）。これは worktree の環境固有の問題で、
  用意した typecheck 用の壊れたファイル（`tests/test_tmp198.py`）が
  原因ではない
- **typecheck は走った形跡が無い**（typecheck のタスク名がログに出ていない）
- **pytest は走らなかった。** `passed` などの pytest 出力は一切出ていない
- **mise は `ERROR task failed` を出して全体を止めた。** `test` タスクの
  依存関係のうち 1 つ（`fmtjs`）が失敗した時点で、以降の依存タスク
  （`typecheck`・`lintjs`・`lint`・`test` 本体の pytest）は実行されなかった

## 結論

**pytest は走らなかった。** 依存タスクが 1 つでも失敗すると `mise run test`
は残りを実行せず終了ステータス 1 で止まる、という実測結果になった
（今回失敗したのは fmtjs で、typecheck ではないが、依存失敗時に
下流タスクが止まる、という確かめたい挙動自体は再現できた）。

## 片付け

```
git -C ~/work/ytsched worktree remove --force /tmp/.../scratchpad/wt198
```
実行済み。
