# TODO-093 の分担

## 誰にどこを

| 担当 | 範囲 | 報告 |
|---|---|---|
| implementer | `state.js` / `main.html` / `main-page.js` / `week.js` / `nav.js` の実装と、`test_main_handler.py` のテスト修正 | [implementer-report.md](implementer-report.md) |
| verifier | lint・型・`test`・`test_browser.py`（3 回）・アプリ起動の確認 | [verifier-report.md](verifier-report.md) |
| wording | コミットに入る `.md` 6 本の前例の無い語 | [wording-report.md](wording-report.md) |

依頼書: [implementer-brief.md](implementer-brief.md) / [verifier-brief.md](verifier-brief.md)

## この分担にした理由

- 5 つの `.js` とテンプレートとテストにまたがるので、実装を
  implementer に分けた（`~/.claude/CLAUDE.md` の「複数のファイルに
  またがる」の目安）。
- 挙動は変えない変更なので reviewer は入れていない
  （TODO-017 の基準：挙動や分岐が変わる項目に入れる）。ブラウザ側の
  退行は `test_browser.py`（TODO-056）で拾えるため、verifier に
  そちらを重点的に走らせた。
- `.md` が入るコミットなので wording を立てた（CLAUDE.md）。

## main が単独で決めたこと

- `#date_from` の hidden の値を `#week_wrap` の `data-monday` に移した
  （空の要素を新しく作らず、その値を持つべき週の入れ物に付けた）。
- 初回ロードで `cur_day` が基準日でなく月曜で送られる差は、TODO 本文が
  承知のうえなのでそのまま。
- wording の指摘のうち「seed」を和語（「入れる」）に、「1 本化」を
  既出の「一本化」に、「種としての値」を「初期値」に直した。残りは
  造語ではないのでそのまま。
- `test_browser.py::test_tap_again_stops_auto_page_turn` の flaky は
  TODO-093 由来ではない（クリーンな `develop` でも落ちる）。別項目は
  立てず、TODO-084 の既知の弱さとして扱う。
