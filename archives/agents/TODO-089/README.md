# TODO-089 の分担

`edit.html` のインライン JavaScript を `static/js/edit-page.js` へ出す
（`main-page.js` と同じ形に揃える）。

## 編成

| 担当 | やったこと |
|---|---|
| implementer | `edit-page.js` の新規作成、`edit.html` の差し替え、`onloadHdr`→`onloadEdit` の改名、未使用リスナーの削除、`src/README.md` の追随 |
| verifier | lint・typecheck・test、アプリ起動での編集画面の目視、元のインライン `<script>` との字句一致の確認 |

## この分担にした理由

- 挙動を変えない切り出しだが、新しい `.js` を 1 本増やす。TODO-083 で
  「`.js` の本数を変える変更は、テストが通っても 404 に気づけない」と
  分かっているので、アプリを起動して `edit-page.js` が 200 で返ることまで
  見る verifier を分けた
- 変更は 2 ファイル（＋文書の追随）で、実装とテストと文書がまとまって
  要るわけではないので、reviewer は付けなかった。字句一致の確認を
  verifier の依頼に含めることで、「本体を変えていない」ことは押さえられる

## 報告

- [`implementer-report.md`](implementer-report.md)
- [`verifier-report.md`](verifier-report.md)
- [`wording-report.md`](wording-report.md)
