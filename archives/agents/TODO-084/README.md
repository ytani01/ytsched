# TODO-084 の分担

フッターの ◀ ▶ をダブルタップして自動ページ送り。

| 担当 | 何を任せたか |
|---|---|
| main | 仕様の具体化（`conf.json` のキー名・既定値・範囲、止め方、下限の根拠）と、依頼書 |
| implementer | Python・テンプレート・`static/js/`・テストの実装 |
| verifier | `mise run fmt` / `typecheck` / `lint` / `test` と、実際のブラウザでの動き |
| reviewer | 変更したコードの質 |
| wording | コミットに入る `.md` の、前例の無い語 |
| writer | `src/README.md` と archives の文書 |

## この分担にした理由

- **implementer を分けた。** Python（`MainHandler` の設定の読み方）・
  テンプレート・`static/js/` の 2 本・テスト 2 本にまたがる。
  複数のファイルにまたがり、実装とテストがまとまって要る項目
  （`~/.claude/CLAUDE.md` の目安）。
- **reviewer を入れた。** ボタンの入力の拾い方を `onmousedown` から
  `pointerdown` / `pointerup` へ変える。**挙動と分岐が変わる**ので、
  TODO-017 で決めた起用の基準に当たる。`swipe.js` が `mousedown` を
  capture で止めて離したときに呼び直す仕掛けと、二重に効かないかを
  見てもらう必要がある。
- **verifier を分けた。** ブラウザを動かすテスト（TODO-056）があり、
  実際に試せる手順がある。TODO-017 の「試せる手順があるなら分ける」に
  当たる。既存の `#forward_button` を続けて叩くテストが、
  ダブルタップと見分けが付かなくなって落ちる見込みだったのも理由。
- **wording を立てた。** `.md` が入るコミットなので（TODO-025・TODO-026）。
  項目を立てたときの分は `wording-report.md` にある。

## 報告

- [`request-implementer.md`](request-implementer.md) — implementer への依頼書
- [`implementer-report.md`](implementer-report.md)
- [`verifier-report.md`](verifier-report.md)
- [`reviewer-report.md`](reviewer-report.md)
- [`wording-report.md`](wording-report.md) — 項目を立てたときの分
- [`wording-report-2.md`](wording-report-2.md) — 実装したあとの分
