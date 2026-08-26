# TODO-057 の分担

## どう分けたか

| 担当 | 依頼書 | 報告 |
|------|--------|------|
| wording（決めごとのコミット） | — | `wording-report.md` |
| implementer（1 回目） | `request-implementer.md` | `implementer-report.md` |
| reviewer | `request-reviewer.md` | `reviewer-report.md` |
| implementer（2 回目・指摘の修正） | `request-implementer-2.md` | `implementer-report-2.md` |
| verifier | `request-verifier.md` | `verifier-report.md` |

決めごとそのもの（何をどう作るか）は main が利用者と決めた。

## その分担にした理由

- **implementer を分けた。** 触るのが `my.js`・`main.html`・`my.css`・
  `main_handler.py` の 4 ファイルにまたがるため。項目を立てたときの
  見込みは `main のみ` だったが、着手時に書き直した
- **reviewer を入れた。** 挙動と分岐が変わる項目だから（TODO-017）。
  実際、`slideWeekWrap()` の呼び出しが重なると `on_done()` が二重に
  呼ばれる不具合を見つけた。**テストが通ることを見ても出てこない種類の
  指摘**で、`test` 439 件はこの不具合があっても全部通っていた
- **verifier を分けた。** 見た目と指の操作は、テストでは確かめられない。
  `tests/` にブラウザを動かすテストがまだ無い（TODO-056）ので、
  playwright を手で動かす必要があった
- **reviewer を verifier より先に走らせた。** 並行で走らせたが、
  verifier が 1 回目にセッションの上限で落ちたため、結果として
  「reviewer の指摘を直してから verifier」の順になった。**この順のほうが
  良かった**。verifier が確かめる対象が、直したあとのコードになる

## 気づいたこと

- **reviewer と verifier を並行で走らせると、reviewer の指摘で直した分を
  verifier が見ていないことになる。** 今回はたまたま直列になったが、
  次からは意図してこの順にしたほうがよさそう
- **implementer は「実機の見た目を確かめる手段が無い」と正直に書いて
  きた。** 埋めずに verifier へ渡したのは正しい振る舞い
