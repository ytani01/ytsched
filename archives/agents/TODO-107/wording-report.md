# TODO-107 文書語彙確認

`git diff --cached --name-only -z -- '*.md'` で得た次の 8 ファイルを読んだ。

- `TODO.md`
- `archives/agents/TODO-107/README.md`
- `archives/agents/TODO-107/implementer-report.md`
- `archives/agents/TODO-107/reviewer-report.md`
- `archives/agents/TODO-107/verifier-report.md`
- `archives/agents/TODO-107/wording-report.md`
- `archives/todo/TODO-107. JavaScript のグローバルスコープ整理と ESLint ルール有効化.md`
- `src/README.md`

## 前例のない語

| 語 | 出てくるファイルと箇所 | HEAD の前例 | 見立て |
| --- | --- | --- | --- |
| 即時実行関数 | `archives/todo/TODO-107. JavaScript のグローバルスコープ整理と ESLint ルール有効化.md:19` | 前例なし | IIFE を指す一般に通用する IT 用語に見える。 |
| 公開名への移行 | `archives/agents/TODO-107/implementer-report.md:16` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 一貫した移行 | `archives/agents/TODO-107/implementer-report.md:23` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 中途変更 | `archives/agents/TODO-107/implementer-report.md:23` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 共有作業ツリー | `archives/agents/TODO-107/implementer-report.md:24` | 前例なし | Git の worktree を説明する一般的な言い方に見える。 |
| イベント処理 | `archives/agents/TODO-107/reviewer-report.md:12` | 前例なし | 一般に通用する IT 用語に見える。 |
| 時間上限 | `archives/agents/TODO-107/verifier-report.md:7, 17` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 全件の結果 | `archives/agents/TODO-107/verifier-report.md:7` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 個別実行 | `archives/agents/TODO-107/verifier-report.md:17` | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 取り残し | `archives/agents/TODO-107/README.md:9` の「公開名の取り残し」 | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |
| 中途で停止 | `archives/agents/TODO-107/README.md:10` の「implementer が中途で停止」 | 前例なし | 一般的な日本語で、リポジトリ固有の言い換えには見えない。 |

前例のない語は 11 語。`window.ytsched`、公開範囲、名前空間、公開名、
インラインイベント、`page.evaluate()`、`auto_turn_msec`、ブラウザテストから
直接使う関数・定数名には、HEAD の Markdown に前例がある。
