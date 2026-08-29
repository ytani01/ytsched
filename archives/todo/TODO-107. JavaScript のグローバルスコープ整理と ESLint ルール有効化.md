# TODO-107. JavaScript のグローバルスコープ整理と ESLint ルール有効化

|      | main | 担当 |
|------|------|------|
| 見込み | GPT-5 / effort high | implementer + verifier + reviewer |
| 実施 | GPT-5 / effort high | main + implementer + verifier + reviewer + wording |

## きっかけ

JavaScript の関数・状態・テンプレートから渡す値がグローバルスコープに散らばり、
ESLint の `no-undef` と `no-unused-vars` を有効にできなかった。

分担と各担当の報告は
[archives/agents/TODO-107](../agents/TODO-107/README.md) にまとめた。

## やったこと

- ファイル間で共有する関数・状態とテンプレート値を `window.ytsched` の下に置き、
  ファイル内だけで使う名前は即時実行関数で閉じた。
- `main.html`、`edit.html`、`sde.html` のインラインイベントと、ブラウザテストの
  `page.evaluate()` を `window.ytsched` 経由にした。
- ESLint の `no-undef` と `no-unused-vars` を有効にし、検出された参照と未使用の
  引数を直した。
- 一覧・編集画面の読み込みで `pageerror` が出ないことを確かめるブラウザテストと、
  公開範囲を説明する文書を追加した。

## テスト

- `mise run lintjs`: 合格。
- `uv run pytest tests/test_browser.py -v`: 25 件すべて合格。
- reviewer: 指摘なし。
