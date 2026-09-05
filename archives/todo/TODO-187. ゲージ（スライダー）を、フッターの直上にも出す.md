# TODO-187. ゲージ（スライダー）を、フッターの直上にも出す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier ×2 + reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 22,704 | 185,679 | 37% |
| implementer | Opus 5 | medium | 12,844 | 181,013 | 28% |
| reviewer | Opus 5 | high | 24,687 | 100,298 | 26% |
| verifier | Sonnet 5 | medium | 7,100 | 72,603 | 9% |
| 合計 |  |  | 67,335 | 539,593 | 概算 $9.9 |

- implementer は定義（`.claude/agents/implementer.md`）のモデルが sonnet。
  gauge.js を複数のゲージ前提へ直す変更が込み入るので Opus 5 に上書きした
- reviewer も定義のモデルは sonnet。挙動が変わる項目なので Opus 5 に上書きした
- verifier は定義のまま（Sonnet 5 / effort medium）。2 回動かした
- **implementer は 2 回目の依頼（reviewer の指摘への対応）の途中で、Opus の
  セッション上限（HTTP 429）で終了した。** 何も変更されていなかったので、
  残りは main が直接直した

## きっかけ

上のゲージは画面をスクロールしても見えているが、指はフッターの側にある。
下にも同じものが欲しい。

## やったこと

### 2 つ目のゲージ

`main.html` の `<footer>` の先頭（メニューバーの直前）に、上と同じ中身の
ゲージを置いた。外側は `#footer_gauge_bar.my-footer-gauge-bar`
（`position: fixed` / `z-index: 50`）。上と同じ `{% if not search_mode %}` で
囲んであるので、検索モードでは上下とも出ない。

メニューを開くと `.my-bar-content`（`z-index: 100`）がせり上がって
下のゲージを隠す。`.my-menu-bar` は `z-index: 200` なので、メニューバー
そのものは常に下のゲージより前に出る。

`bottom` の既定は CSS で `42px`（閉じたメニューバーの高さ）にしてある。
実際の値は `onloadHdr()` が `#menu_bar` の高さを実測して入れる
（インラインの指定なので CSS より勝つ）。既定を `0` にすると、読み込みが
遅いときにメニューバーの裏へ潜り込んだゲージが一瞬見えてから飛ぶ
（reviewer 指摘 4）。

`body` の `paddingBottom` は「メニューバーの高さ ＋ 下のゲージの高さ」。
既存の `paddingTop`（上の週バー）と同じく、`body_h` / `win_h` を測るより
先に入れている。

### ゲージが複数ある前提へ

- `#gauge_r` / `#gauge_r_label` の id をやめ、`.my-gauge-r` /
  `.my-gauge-r-label` で引く形に統一した
- `state.js` の `ytState.elGaugeR0`（1 つ）を `elGaugeRs`（配列）にした。
  「検索モードでゲージが無い」の判定は `elGaugeRs.length === 0`
- `gauge.js` に `setGaugeNeedles(rel_days)` と `setGaugeNoTransition(flag)` を
  新設し、針の `left`・ラベルの文字・`my-gauge-r-no-transition` の付け外しを
  すべてのゲージへまとめて反映するようにした
- `dispGaugeMarks()` は `.my-gauge-bar` 全部に目盛りを描く
- `mondayFromClientX()` は帯を引数で受け取る形にした。pointerdown で
  `closest(".my-gauge-bar")` した帯を `gaugeBarDragStart.elBar` に持ち、
  pointermove でもそれを使う。これが無いと、下の帯をドラッグしても
  上の帯の矩形で位置を計算してしまう

上下が同時に操作されたときのことは考えていない。

## テスト

`tests/test_browser.py` の `#gauge_r` / `#gauge_r_label` 14 箇所をクラス指定へ
直した（要素が 2 つになるので locator は `.first`）。足したのは 4 件。

- `test_gauges_are_in_the_header_and_above_the_footer` — 帯が 2 つあり、
  下の帯の下端がメニューバーの上端に接する
- `test_both_gauge_needles_are_at_the_same_position`
- `test_both_gauge_labels_are_the_same_text`
- `test_footer_gauge_drag_moves_to_the_released_week`

それに加えて、reviewer の指摘 2 で assert を 3 つ足した。
`test_gauge_marks_are_drawn_at_the_same_position` にフッター側の目盛り
14 個、`_assert_search_screen()` に `#footer_gauge_bar` と `.my-gauge-bar` が
0 個であること。

- `uv run pytest tests/test_browser.py` … 77 件通過
- `uv run pytest --ignore=tests/test_browser.py` … 611 件通過
- `mise run fmt` / `lint` / `typecheck` … エラーなし
- verifier が実機（幅 390px）で、上下のゲージ・下のドラッグ・メニュー開閉・
  検索モード・スクロールを確認

## 見送ったもの

- **下の帯だけ幅を変えて、`mondayFromClientX()` の矩形の取り違えを捕まえる
  テスト**（reviewer 指摘 3）。上下の帯は幅も左右の位置も同じなので、
  いまのドラッグのテストは矩形を取り違えても通ってしまう。ただし帯の幅を
  テストから書き換える形は実装の内部事情に寄るので、入れないことにした
- **`docs/user-week.png`（利用者向けの画面図）の撮り直し。** 下のゲージが
  写っていない古い画像のまま。別項目にする
- **`main.html` にゲージのマークアップが 2 回ある件。** `{% include %}` に
  切り出す手はあるが、上の方に TODO-066 / 072 / 078 のコメントが
  ぶら下がっていて、説明の置き場所を決め直すことになる。いまは直さない

## 分担の振り返り

- **implementer** は依頼の 7 項目をすべて実装し、`elGaugeRs` の配列化・
  `setGaugeNeedles()` の切り出し・帯の持ち回りまで自分で設計した。
  Opus に上げた判断は当たっている。同時に「下の帯のドラッグテストは
  矩形の取り違えを捕まえられない」と自分の弱点を申告してきた
- **reviewer** は 4 点を指摘し、うち 3 点（文書の食い違い、テストの穴 2 つ、
  CSS の既定位置による読み込み中のちらつき）を採った。とくに
  「`dispGaugeMarks()` が上だけに描いてもどのテストも落ちない」は、
  テストが 77 件通ることを見ても出てこない指摘で、入れた価値があった
- **verifier** は 2 回とも「問題なし」で、指摘はゼロ。ただし実機での
  下のゲージのドラッグ・メニュー開閉・検索モードの確認は、テストだけでは
  見ていない範囲で、分けた意味はあった
- **見込みとの食い違いは 2 つ。** verifier を 2 回動かしたこと（reviewer の
  指摘に対応したので、その確認が要った）と、implementer が Opus の
  セッション上限で 2 回目の依頼を落としたこと
- 次に同じ規模（複数ファイルにまたがる UI の追加、テストの書き換えを伴う）を
  やるなら、同じ `implementer + verifier + reviewer` でよい。ただし
  **reviewer の指摘への対応が小さいときは、implementer を再開せず main が
  直接直すほうが安い**（今回は結果的にそうなった）。implementer を Opus に
  上げると上限に当たりやすいので、2 回目の依頼を出す前に残量を見ること
