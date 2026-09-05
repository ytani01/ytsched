# TODO-184. 週送りのあと、画面の下部が灰色にならないことがある

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 8,227 | 22,232 | 52% |
| implementer | Sonnet 5 | medium | 3,534 | 41,934 | 12% |
| verifier | Sonnet 5 | medium | 4,946 | 37,526 | 17% |
| reviewer | Sonnet 5 | high | 14,253 | 66,283 | 19% |
| 合計 |  |  | 30,960 | 167,975 | 概算 $2.1 |

- 3 担当とも定義ファイル（`.claude/agents/*.md`）のモデル・effort のまま。
  上書きはしていない

## きっかけ

一覧画面の下部が灰色にならず、フッターとの間に白が残ることがある、と
スマホの画面で報告があった。

一覧の地の色 `--my-cal-ground` は `#main` にだけ付いていて、`body` は白。
中身が画面より短いときに白が残らないよう、`main-page.js` の `onloadHdr()` が
`#main` の `minHeight` を計算して伸ばしていた（TODO-176）。

これが**読み込み時に一度しか走らず**、しかも `body_h < win_h` のときだけ
走っていた。週の高さは `.my-week-panel` の切り替えで変わる（通常フローに
居るのは今の週だけ）ので、読み込み時に予定の多い週を見ていると `minHeight`
が付かず、そこから予定の少ない週へ送ったときに白が残る。画面の高さが変わる
とき（回転、アドレスバーの出入り、キーボードの開閉）も同じ。

## やったこと

- `main-page.js` に `window.ytsched.fillMainHeight()` を切り出した。
  **測る前に `minHeight` を空へ戻す**（前の値が残っていると `body_h` を
  正しく測れない）。そのうえで `body_h < win_h` なら、これまでと同じ式で
  `minHeight` を入れる
- `week.js` の `setActiveWeek()` から呼ぶ。**`scrollToId()` より先**に置く
  （下記）
- `window` の `resize` / `orientationchange` からも呼ぶ。`elMain` は
  `onloadHdr()` で入るので、まだ無ければ何もしない
- `onloadHdr()` は、`minHeight` を入れていた所をこの関数の呼び出しに
  置き換えた。読み込み時の分かれ方（短いときは visible → `dispGauge()` →
  return、長いときは `scrollToDate()` を通る）は変えていない

CSS だけで `#main { min-height: 100dvh }` とする案は見送った。`body` に
週バーとメニューバーぶんの padding が入るので、縦スクロールが余分に出る。

### 呼ぶ位置を `scrollToId()` の前にした理由

管理者は当初、`scrollToId()` の**あと**に置くよう依頼した。`scrollToId()` が
`body_h <= win_h` を見て早く返すので、その判定より先に高さを足すと挙動が
変わると考えたため。これは誤りで、reviewer の指摘 1 で入れ替えた。

先に `fillMainHeight()` を通せば、`minHeight` を空へ戻して測り直したうえで
`body_h` はちょうど `win_h` になるので、`scrollToId()` の早い return は
そのまま効く。逆にあとに置くと、**前の週の `minHeight` が残ったまま**測られ、
画面に収まる週でも「収まっていない」と判定されて、要らないスクロールが
起きる。

### 見送った指摘

- **`resize` の間引き**（reviewer 指摘 3）。アドレスバーの出入りのたびに
  走るが、やっているのは `minHeight` の読み書きだけで、見た目が壊れる
  ものではない。実際に重いと分かってから考える
- **`onloadHdr()` に残る `body_h` / `win_h` の二重計算**（同 4）。分岐
  そのものは `fillMainHeight()` の外に残す必要があり、間に高さを変える
  DOM 操作は無い。冗長なだけなので、そのままにした

## テスト

- `mise run fmt` / `lint` / `typecheck` — 通る
- `uv run pytest` — 679 件すべて通る（verifier）。呼ぶ位置を入れ替えた
  あとに `tests/test_browser.py` の 72 件を走らせ直し、通ることを確かめた
- アプリの起動と一覧画面の表示（`--datadir` は一時ディレクトリ）— 例外なし

## 分担の振り返り

- **reviewer が指摘 1 を見つけた。** これは管理者が依頼文で名指しで
  「`scrollToId()` のあとに置くこと」と指示した箇所で、その指示自体が
  間違っていた。implementer は指示どおりに書き、verifier は「依頼の
  とおりに入っているか」を確かめたので、両者とも捕まえられない。
  **依頼文の指示が誤っている可能性は、reviewer だけが拾える。**
  指摘 2（`elMain` の null チェック）も reviewer
- **verifier の発見はゼロ**（テストと lint とアプリ起動はすべて素通り）。
  ただし呼ぶ位置を直したあとのブラウザテストは効いており、置き方だけの
  変更でも 72 件が通ることを確かめる価値はあった
- **見込みと食い違わなかった。** 3 担当とも見込みどおりで、モデルの
  上書きも要らなかった
- **次に同じ規模（JS 2 ファイル、挙動が変わる）をやるなら、同じ組み方で
  よい。** ただし main が 52% を占めたので、依頼文を書く前の下調べを
  減らす余地はある。今回は原因の特定まで main がやってから implementer
  へ渡したが、原因が読みだけで分かる程度なら、調査ごと implementer に
  渡して報告を受けるほうが安い。逆に、**依頼文に「この順序で」と書く
  ような具体的な指示を入れたときは、reviewer を必ず入れる**
  （今回それが効いた）

分担の理由と各担当の報告は `archives/agents/TODO-184/` にある。
