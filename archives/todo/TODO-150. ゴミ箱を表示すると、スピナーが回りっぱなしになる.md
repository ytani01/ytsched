# TODO-150. ゴミ箱を表示すると、スピナーが回りっぱなしになる

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | main のみ + verifier |

## きっかけ

ゴミ箱を表示すると、読み込み中スピナーが回りっぱなしになる不具合が
報告された。

## やったこと

`main-page.js`/`edit-page.js` は `load` ハンドラの最後で
`ytsched.loadingSpinner(false)` を呼び、スピナーを隠している。
`trash-page.js` は TODO-149 で `elLoadingSpinner` をセットする行を
足しただけで、隠す呼び出しを足し忘れていた。スピナーの `div` は
CSS 上デフォルト表示のままなので、ゴミ箱を開くたびに回りっぱなしに
なっていた。

- `trash-page.js` の `load` ハンドラに
  `window.ytsched.loadingSpinner(false);` を追加した
  （`elLoadingSpinner` をセットした直後）

## テスト

- `mise run test` … 597 件全通過
- `mise run lint`（ruff / eslint / basedpyright / mypy） … 通過
- verifier が Playwright + chromium で `/ytsched/trash` を開き、
  `#loadingSpinner` の `getComputedStyle().display` を確認。
  修正後は `'none'`（消える）、`git stash` で修正前に戻すと
  `'block'`（回りっぱなし）になることを確認し、不具合の再現と
  修正の効果を両方確かめた
