# TODO-215. 更新した日付と予定の点滅を分かりやすくする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus / high）+ verifier（Sonnet / medium） |
| 実施 | Opus 5.5 / effort medium | main（実装）+ reviewer（Opus 5.5 / high、再レビュー 1 回）+ verifier（Haiku 4.5） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| reviewer | Opus 5.5 | high | 76 | 350 | 96,216 | 2,156,627 | 49% |
| main | Opus 5.5 | medium | 56 | 13,351 | 30,350 | 1,917,896 | 43% |
| verifier | Haiku 4.5 | 記載なし | 114 | 657 | 29,388 | 319,368 | 8% |
| 合計 |  |  | 246 | 14,358 | 155,954 | 4,393,891 | 計 4,564,449 |

- verifier は定義のモデルが sonnet。定型の実行だけなので Haiku 4.5 に上書きした
  （`CLAUDE.md` の TODO-203 の決まり）。Haiku は effort に対応しないので「記載なし」

## きっかけ

TODO-213 で入れた点滅（3 秒で 3 回、1 回約 0.5 秒）が分かりにくいと
利用者から言われた。キーフレームの間で色が補間され、全体に `ease-out` も
かかるので、黄色がはっきり出ている時間が短い。

フェード（濃い黄色から数秒かけて消す）も案に出したが、利用者が点滅だけを
選んだので採らなかった。

## やったこと

- `src/ytsched/webroot/static/css/my.css`: `.my-flash` を
  `animation: my-flash calc(5s / 6) step-end 6` にし、キーフレームを
  「0% 黄 / 50% なし」の 1 周期にした。全体で 5 秒、約 0.83 秒周期で 6 回、
  中間の色を出さない
- `src/ytsched/webroot/static/js/main-page.js` の `flashUpdated()`:
  予定の行（無ければ日付の欄）が、上の `#week_bar` の下端と下の
  `#footer_gauge_bar`（検索モードでは `#menu_bar`）の上端の間に入るよう
  `scrollBy` する。下にはみ出すなら下端を、上が隠れるなら上端を優先して
  見せる。余白は `scrollToId()` と同じ 30px
- `tests/test_browser.py`: `test_flash_scrolls_sde_between_bars` を足した
  （予定 40 件の日、`sde_align=top` で末尾、`bottom` で先頭の予定）。
  点滅が終わるのを待つテストの timeout を 6 秒から 8 秒にした

当初は `scrollIntoView({block: "nearest"})` を最初の要素（日付の欄）に
かける予定だったが、reviewer の指摘で変えた（下記）。

## 確かめたこと

- reviewer が Chromium で実測: 約 0.83 秒周期で 6 回、中間色なし、
  class は 4.95 秒で外れる
- 再レビューで、週の 4 日 × 先頭・末尾の予定 × top / bottom / home で、
  予定の行が帯の間に入ることを実測。検索モードでもメニューバーより上に出る
- 足したテストは、スクロールの行を消すと `top` の場合が、上端を優先する
  `Math.min` を消すと `bottom` の場合が落ちることを main が確かめた
- verifier: fmt・lint・typecheck は問題なし、テストは 720 件通過

## 残ること

- `calc(5s / 6)` を iOS Safari が受け付けるかは確かめていない
  （受け付けないと点滅しなくなる。reviewer の確信度の低い指摘）

## 分担の振り返り

- **reviewer:** `scrollIntoView` の案の不具合を 2 つ見つけた。
  1 つは、予定の多い日に日付の欄が固定の帯の裏へ隠れる退行。
  もう 1 つは、対象が日付の欄なので普段は何もしないこと。
  さらに、テストがスクロールの処理を通っていないことと、再レビューで
  上が隠れる分岐がテストされていないことを見つけた。どれも直した
- **verifier:** 問題を見つけなかった（定型の実行で、全部通った）
- **見込みとの食い違い:** reviewer が 2 回になった。スクロールの方式を
  固定の帯を考えずに決めたため。verifier は Haiku に下げた
- **次に同じ規模なら:** スクロールや位置合わせを入れるときは、main が
  実装の前に固定の帯（`#week_bar` / `#footer_gauge_bar` / `#menu_bar`）と
  `scrollToId()` の位置合わせを読んでおく。そうすれば reviewer は 1 回で済む。
  reviewer の分が全体の約半分なので、ここを減らすのが一番効く
