# TODO-142. ゴミ箱ヘッダーのチェックボックスに部分選択の「-」を表示しない

|        | main                  | 担当                              |
| ------ | --------------------- | --------------------------------- |
| 見込み | GPT-5 / effort medium | implementer + verifier + reviewer |
| 実施   | GPT-5 / effort medium | implementer + verifier + reviewer |

分担の理由、依頼、報告は
[archives/agents/TODO-142/README.md](../agents/TODO-142/README.md) にある。
`tools/token-usage.py` は Claude Code の transcript を集計する仕組みで、
Codex で行ったこの項目は集計できないため、消費の行は省いた。

## きっかけ

ゴミ箱で複数項目の一部だけを選択したとき、ヘッダーの全選択チェックボックス
に indeterminate 状態の「-」が表示されていたが、この表示は不要との要望が
あった。

## やったこと

- 選択状態を更新するとき、ヘッダーのチェックボックスの `indeterminate` を
  常に `false` にした
- 一部だけ選択したときはヘッダーを通常の未選択表示にし、表示中の全項目を
  選択したときだけ選択済み表示にした
- ヘッダーによる全選択・全解除、項目の選択状態、削除ボタンの有効化、
  選択件数入りの確認、一括削除の処理は変更していない
- ブラウザテストを更新し、部分選択で未選択かつ indeterminate でないこと、
  全選択と全解除、それぞれの削除ボタン状態を確認するようにした
- 利用者向け文書は部分選択の表示方法に触れていないため、変更していない

## テスト

- implementer: 対象ブラウザテスト 2 件 — 通過
- implementer: Prettier、ESLint、`git diff --check` — 通過
- main: `uv run pytest tests/test_browser.py -k 'trash_select' -q` —
  2 件通過、48 件除外
- main: Prettier、ESLint、`git diff --check` — 通過
- verifier: `uv run pytest tests/test_browser.py -k 'trash_select' -q` —
  2 件通過、48 件除外
- verifier: `mise run test` — Ruff、Prettier、ESLint、basedpyright、mypy、
  pytest 583 件がすべて通過
- verifier: `git diff --check` — 通過
- reviewer: 指摘なし
