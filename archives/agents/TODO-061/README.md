# TODO-061 の分担

## どう分けたか

| 担当 | 依頼書 | 報告 |
|------|--------|------|
| verifier | `verifier-request.md` | `verifier-report.md` |
| wording | — | `../TODO-062/wording-report.md` |

実装は main が行った。見込みの `main のみ + verifier` のとおり。

## その分担にした理由

- **implementer を分けなかった。** 触るのが `my.css` と `main.html` の
  2 ファイルで、変更は CSS の値と、包む `<div>` を 1 つ足すだけだった
  ため
- **verifier を分けた。** 見た目は、実装した本人が「直ったはず」で
  済ませてしまう。とくに `overflow-x: clip` がスワイプ（TODO-054・
  TODO-057）を壊していないかは、指の操作を組み立てて確かめる必要が
  あった
- **reviewer は入れなかった。** 分岐も挙動も変わらず、CSS の値と
  切り取る位置だけの変更のため（TODO-017 の基準）
- **wording は TODO-062・TODO-063 を立てるコミットで立てた。**
  報告はそちらのディレクトリにある

## 気づいたこと

- **verifier に「心配なところ」を名指しで書いたのが効いた。**
  依頼書に「`overflow-x: clip` で隣の週まで切れていないかが心配」と
  書いたので、`touchmove` を組み立てて追従とスクロール幅の両方を
  確かめてきた
- **TODO-054 の verifier 報告に書いてあったスワイプの手順を、依頼書から
  参照して使い回せた。** 手順を書き写さずに済んだ
