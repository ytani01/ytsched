# TODO-152 の分担

項目は
[TODO-152. docs/User.md に画面図を入れる](../../todo/TODO-152.%20User.md%20に画面図を入れる.md)。

| 担当 | やったこと |
|------|------------|
| main | サンプルデータの用意、6 画面の撮影、`tools/annotate.py` と `tools/user-figs.json`、`docs/User.md` の書き直し、`docs/Developer.md` と `mise.toml` |
| verifier | [verifier-report.md](verifier-report.md) |

## この分担にした理由

TODO-151 と同じで、図を作る作業は一続きで受け渡すところが無いので main が
やった。**作った本人には、図が期待どおりかを見きれない**（自分で置いた
吹き出しは、置いたつもりの場所に見えてしまう）ので、はみ出し・線のずれ・
文字切れと、本文と実装の食い違いは別の担当に見させた。

依頼は [verifier-request.md](verifier-request.md)。撮り直しの手順
（サンプルデータ、URL、それぞれの高さ、撮る順番）もそこに書いてある。

## verifier の指摘への対応

- `docs/user-search.png` の左側の引き出し線 3 本が交差して追いにくい
  → 「さかのぼった一番古い日」と「いま出ている結果より…」の上下を
  入れ替えて解消した（`tools/user-figs.json`）
- `docs/Developer.md` が指す `archives/todo/TODO-152. ….md` が無い
  → 決着時に作るファイルなので、そのまま
