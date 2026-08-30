# TODO-106. MainHandler の引数解析とビューモデル構築の分離

|      | main | 担当 |
|------|------|------|
| 見込み | Gemini 3.7 Flash / effort high | implementer + verifier + reviewer |
| 実施 | GPT-5.6 / effort high | main + implementer + verifier + reviewer |
| 消費 | 記録不可 | Codex の transcript は `mise run tokens` の対象外 |

分担と各担当の報告は
[archives/agents/TODO-106](../agents/TODO-106/README.md) にまとめた。

## きっかけ

`MainHandler` に集中していた引数解析・検証と、一覧表示用データの組み立てを
分離し、HTTP の受付・更新実行・リダイレクトだけを担う構成にする。

## やったこと

- `MainBinder` を追加し、フォーム・クエリ引数、設定値、正規表現の解析と
  検証、更新フォームの組み立てを移した。
- `MainViewBuilder` を追加し、ToDo、週間表示、月間ミニカレンダーと
  テンプレート引数の組み立てを移した。
- `MainHandler` を GET/POST、更新コマンド、リダイレクトに絞った。
- 設定の保存、入力エラーの順序、既存の定数と `months2weeks()` の参照先を
  保つテストと説明を更新した。

## テスト

- `mise run lint`: Ruff、Prettier、ESLint、basedpyright、mypy が合格。
- `uv run pytest tests --ignore=tests/test_browser.py -q`: 483 passed。
- `uv run pytest tests/test_browser.py -q`: 26 passed。
- verifier: 一時データディレクトリで一覧・検索・編集画面を取得し、すべて
  HTTP 200、入力エラーは HTTP 400 を確認。修正後に lint と対象184件も再確認。
- reviewer: 引数解析と表示データの責務境界、既存の HTTP 挙動、設定保存を確認し、
  指摘なし。
