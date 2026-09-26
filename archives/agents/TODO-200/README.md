# TODO-200 の分担

- main: 実装（2 か所の変更なので分けなかった）
- reviewer（Sonnet 5 / high）: `data-action` の分岐が変わるので、mousedown と
  change の両方で拾われる要素がほかに無いかを見た → [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5 / medium）: Playwright で、`<select>` を押しただけでは
  読み直されないこと、選ぶと `conf.json` に保存されること、フィルタのアイコンが
  今までどおり送信することを実測した。変更前に戻して不具合の再現も見た
  → [verifier-report.md](verifier-report.md)（スクリプトは `verifier-check*.js`）
