# TODO-083 の分担

`my.js`（1,399 行）を 8 本に分け、`main.html` の `<script>` を
`main-page.js` へ移した項目。

## なぜこの分担にしたか

- **implementer を分けた。** 触るファイルが 8 本の新規 `.js` と
  テンプレート 3 つにまたがり、`ytState.` への書き換えが 58 か所ある。
  機械的だが量が多く、main が直接やると会話が長くなる
- **verifier を立てた。** `.js` を 1 本から 8 本に増やしたので、
  **どれか 1 本でも 404 になれば、テストが 1 件も落ちないまま画面が
  動かなくなる**。テストが通ることを見ても
  出てこない種類の失敗なので、実際にアプリを起動して
  8 本すべてのステータスとブラウザのコンソールを見させた
- **reviewer を入れた。** 「挙動は変えない」が前提のリファクタリング
  なので、元の `my.js` と新しい 8 本を突き合わせて、`ytState.` を
  付ける以外の差が無いことを確かめる担当が要る。
  `~/.claude/CLAUDE.md` の基準では「挙動や分岐が変わる項目には入れる」だが、
  ここは逆に**変わっていないことを示すため**に入れた
- **runner を追加で立てた。** reviewer の指摘（コメント 4 か所）を
  main が直したあと、決まった手順（lint / typecheck / test）を
  走らせ直すだけだったため

## 依頼書と報告

- [implementer-request.md](implementer-request.md) /
  [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md) /
  [verifier-report.md](verifier-report.md)
- [reviewer-request.md](reviewer-request.md) /
  [reviewer-report.md](reviewer-report.md)
- [runner-report.md](runner-report.md)

## 結果

- implementer — 依頼どおりに分割。`// declared in my.js` を
  `// declared in state.js` に直した判断だけを報告してきた
- verifier — 475 件通過（`test_browser.py` の 19 件も skip なし）、
  8 本すべて 200、コンソールエラー 0 件
- reviewer — **挙動の変化は無し**（元と新を結合して機械的に差分を取り、
  関数・定数の中身が 1 バイトも変わっていないことを確認）。
  指摘は、削除した `my.js` を指すコメントが 2 か所残っている件と、
  `activeWeekOffset` の説明コメントが `state.js` へ移すときに
  消えている件の 3 つ。**どれも main が直した**
