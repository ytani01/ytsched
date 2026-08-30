# TODO-117 の分担

implementer が実装とテストの追加、verifier が確認を担当した。TODO-116 と
同じ編成。

JavaScript 4 ファイル (`week.js`・`keyboard.js`・`swipe.js`・`main-page.js`)
とブラウザーテストにまたがるので、実装を分けた。TODO-116 で設計は
決まっていたため reviewer は入れていない。

verifier には、**一覧画面 (検索していない状態) の挙動が変わっていないこと**
を重点的に確かめさせた。共通の関数へ切り出す変更で、検索していないときの
経路まで巻き込む恐れがあったため。あわせて、追加したテストが実装を壊した
ときに実際に落ちるかも確かめさせている。

途中で「検索モードでは PC のマウスドラッグが `swipeFinish()` に届かない」
ことが分かり、利用者に確かめた上で追加で直した (追従表示は出さず、タッチと
同じ挙動に揃える)。

報告:

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
