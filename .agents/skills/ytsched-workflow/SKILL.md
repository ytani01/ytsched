---
name: ytsched-workflow
description: >-
  ytsched リポジトリでの TODO 立案、実装、検証、レビュー、トークン集計、
  および 2段階コミットの標準ワークフローを実行する際に使用する。
---

# ytsched Standard Workflow

ytsched プロジェクトにおける開発・タスク管理の標準手順。

## 1. タスク立案時 (TODO.md)

1. `TODO.md` の「残っている項目」リストと「番号は `TODO-NNN` から」を確認。
2. 計画を作成し、見込み行（モデル・担当）を添えてユーザーに提示、承認を得る。
3. `TODO.md` に項目を追加。
4. コミット（立案時）:
   ```bash
   git commit -m "docs(todo): …の件を TODO-NNN として立てる"
   ```

## 2. 実装と検証の分離

1. **実装 (`implementer`)**:
   - `TODO.md` の該当項目範囲のみを変更。
   - 変更後は自分でも基本動作を確認。
2. **検証 (`verifier` / `runner`)**:
   - `runner`: `ruff`, `basedpyright`, `mypy`, `pytest` を定型実行。
   - `verifier`: `--datadir <一時ディレクトリ>` を用いてアプリの起動・curl 検証・テストを実行。
3. **レビュー (`reviewer`)**:
   - `git diff` を確認し、設計・正しさ・規約逸脱をチェック。

## 3. 完了記録とコミット

1. `archives/todo/TODO-NNN. タイトル.md` を作成（きっかけ、やったこと、テスト、見込み/実施/消費トークン表）。
2. `TODO.md` から完了項目を目次（`## 完了済み`）へ移動。
3. コミットに対象 `.md` が含まれる場合は `wording-check` スキルで語彙確認。
4. コミット（完了時）:
   ```bash
   git commit -m "feat(...): …（TODO-NNN）"
   ```
