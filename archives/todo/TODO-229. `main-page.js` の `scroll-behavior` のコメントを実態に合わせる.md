# TODO-229. `main-page.js` の `scroll-behavior` のコメントを実態に合わせる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort 不明 | main（実装）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | 不明 | 53 | 18,617 | 27,334 | 2,742,658 | 82% |
| ver-229（verifier） | Sonnet 5.5 | medium | 34 | 7,176 | 39,931 | 548,359 | 18% |
| 合計 |  |  | 87 | 25,793 | 67,265 | 3,291,017 | 計 3,384,162 |

- TODO-231・TODO-232 と同時に進めたので、集計の範囲が重なっている。main と verifier は 3 項目で共通

## きっかけ

TODO-227 のレビューで、コメントが理由に挙げる Bootstrap の `scroll-behavior` が CSS に無いと分かった。

## やったこと

- `src/ytsched/webroot/static/js/main-page.js`: 読み直し後の `"instant"` は、`scrollToDate()` の既定が `"smooth"` なので残し、理由のコメントを直した
- 同じファイルの `scrollBy` は指定が要らないので、`scrollBy(0, dy)` にしてコメントを消した

## 確かめたこと

verifier が実際のアプリと chromium で測った（`archives/agents/TODO-229/verifier-report.md`）。

- `scrollBehavior` は `auto`
- `scrollBy` の直後に `scrollY` が 192 から 674 になり、アニメーションしない
- 読み直し後の位置合わせに途中の値は出ない

## 分担の振り返り

- **各担当が見つけたもの:** verifier はこの項目では問題を見つけなかった。同じ確認で TODO-232 のテストの不具合を見つけた
- **見込みと食い違った点:** 無し。見込みどおり reviewer は立てなかった
- **次の編成への指示:** コメントと不要な指定を外すだけの項目は、同じ main と verifier 1 人でよい。測定は代表 1 回ずつで足りた
