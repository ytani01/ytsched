# TODO-184 の分担

一覧画面で `#main` の高さ合わせが読み込み時に一度しか走らず、週送りの
あとにフッターとの間へ白が残る件（TODO.md、`archives/todo/TODO-184. …`）。

| 担当 | 依頼 | 報告 |
|------|------|------|
| implementer | [implementer-request.md](implementer-request.md) | [implementer-report.md](implementer-report.md) |
| verifier | [verifier-request.md](verifier-request.md) | [verifier-report.md](verifier-report.md) |
| reviewer | [reviewer-request.md](reviewer-request.md) | [reviewer-report.md](reviewer-report.md) |

## この分担にした理由

- JS 2 ファイルにまたがり、呼ぶ位置と順序を決める必要があるので、
  実装を implementer に分けた
- **挙動が変わる**（高さ合わせが走る回数と場面が増える）ので、verifier とは
  別に reviewer も入れた
- verifier と reviewer は並行で走らせた。互いの結果に依存しないため

トークンの数字と振り返りは `archives/todo/` 側にある（ここには写さない）。
