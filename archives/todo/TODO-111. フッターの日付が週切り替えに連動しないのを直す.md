# TODO-111. フッターの日付が週切り替えに連動しないのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | GPT-5 / effort high | main + verifier + reviewer |
| 実施 | GPT-5 / effort high | main + verifier + reviewer + wording |

## きっかけ

TODO-110 では `setActiveWeek()` から `document.getElementById("date")` を
更新するようにしたが、`main.html` にはヘッダーとフッターの
`id="date"` が重複していた。このため、先にあるヘッダーの日付入力欄だけが
更新され、フッターの日付入力欄は古い日付のまま残っていた。

分担と各担当の報告は
[archives/agents/TODO-111](../agents/TODO-111/README.md) にまとめた。

## やったこと

- ヘッダーとフッターの日付入力欄の ID を `header_date` と `footer_date` に
  分けた。
- `setActiveWeek()` で、存在する両方の日付入力欄と `#cur_day` を表示中の
  週の月曜に揃えるようにした。
- 検索表示にはヘッダーが無いため、読み込み時の日付参照は
  `#footer_date` に切り替えられるようにした。
- 通常表示の週切り替えと、長い検索結果の読み込みをブラウザテストで
  確認するようにした。
- `src/README.md` の週移動の説明を、新しい ID に合わせた。

## テスト

- 対象ブラウザテスト 3 件: 合格。
- Ruff、Prettier、ESLint、basedpyright、mypy: 合格。
- `mise run test`: 505 件中 504 件が合格。既存の
  `test_tap_again_stops_auto_page_turn` がタイムアウトした。
- 上記を含む自動週送りテスト 2 件を単独で再実行: 2 件とも合格。今回の変更と
  無関係な、実行タイミングに依存する既知の不安定さと判断した。
- reviewer の再レビュー: 指摘なし。
