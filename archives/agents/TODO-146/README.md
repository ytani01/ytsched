# TODO-146 の分担

| 担当 | 何を任せたか | なぜ分けたか |
|------|--------------|--------------|
| implementer | `my.css` とテンプレート 4 枚の書き換え、変更前後の計算値の突き合わせ | テンプレート・CSS・文書がまとまって要り、変更前の状態を先に採る手順もある。main が抱えると差分を全部読むことになる |
| verifier | 独立にテスト・lint を走らせ、アプリを起動して画面を操作 | 実装者は「計算値が合っている」で止まりやすい。メニューと詳細の開閉は `!important` を外した影響が出る場所で、実際に触らないと分からない |
| reviewer | 変更前の `class="..."` をショートハンド込みで展開し、役割クラスの計算値と 1 要素ずつ突き合わせ | 見た目を変えない項目なので、テストでは写し漏れが見つからない。TODO-047 でも同じ照合が効いた |

`main のみ` にしなかったのは、169 か所のクラスを畳み込む項目で、
写し漏れが 1 つでもあると黙って見た目が変わるため。

- [implementer への依頼](implementer-request.md) / [報告](implementer-report.md)
- [verifier への依頼](verifier-request.md) / [報告](verifier-report.md)
- [reviewer への依頼](reviewer-request.md) / [報告](reviewer-report.md)

決着した項目は
[`archives/todo/TODO-146. …`](../../todo/TODO-146.%20CSS%20のクラス名を、Bootstrap%20由来のものからアプリの役割の名前へ変える.md)。
