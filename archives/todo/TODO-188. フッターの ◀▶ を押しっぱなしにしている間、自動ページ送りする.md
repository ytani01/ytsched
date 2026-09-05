# TODO-188. フッターの ◀▶ を押しっぱなしにしている間、自動ページ送りする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ + verifier + reviewer |
| 実施 | Opus 5 / effort high | main のみ + verifier（2 回目は失敗）+ reviewer |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 47,625 | 265,378 | 72% |
| verifier | Sonnet 5 | medium | 12,254 | 211,569 | 17% |
| reviewer | Opus 5 | high | 23,671 | 68,668 | 10% |
| 合計 |  |  | 83,550 | 545,615 | 概算 $14.1 |

- reviewer は定義（`.claude/agents/reviewer.md`）のモデルが sonnet。挙動が
  変わる項目なので Opus 5 に上書きした
- verifier は定義のまま（Sonnet 5 / effort medium）。2 回動かしたが、
  2 回目は堂々巡りになって報告を出せず、main が停止させた

## きっかけ

いままでは「◀▶ のダブルタップで自動送りを始め、もう一度タップで止める」
（TODO-084・TODO-123）だけだった。押している間だけ送って、離したら止まる
ほうが分かりやすい場面がある。

## やったこと

`src/ytsched/webroot/static/js/main-page.js` だけ。

- `PAGE_TURN_HOLD_MSEC`（500）を足し、`pageTurnPointerDownHdr()` で
  長押しタイマーを張る。500msec が経ったらまず 1 週送り、そのあと
  `startAutoPageTurn()` で `AutoTurnMsec` 間隔を張る。
  `setInterval` を張るだけだと、最初の 1 週まで `AutoTurnMsec` ぶん待つ
- `pageTurnPointerMoveHdr()` を新設し、ボタンから 30px 以上ずれたら
  長押しタイマーを消す
- 検索画面（`ytsched.search_date_to`）ではタイマーを張らない。送るたびに
  ページを読み直すので、指を押さえたままの状態が途切れる
- **ダブルタップでの自動送りはそのまま残した。** 手を離しても送り続けたい
  ときに使える

### reviewer の指摘への対応

`autoTurnFromHold` を足して、「押しっぱなしで始めた自動送り」かどうかを
持つようにした。ダブルタップで始めたものは手を離しても続くのが仕様なので、
指を離したかどうかで止めてはいけない。

1. **ボタンの外で離すと止まらなかった**（PC のみ）。`pointerup` の
   「ボタンの上で離したか」の分岐が、自動送りを止める分岐より先にあった。
   押しっぱなし由来なら、その分岐より先に止めるようにした
2. **`pointercancel` のあとに `pointerup` は来ない**ので、割り込まれると
   止める機会が無くなっていた。押しっぱなし由来のときだけ、ここでも止める
3. **自動送り中に「止めるつもりで」500msec 以上押すと、逆に 1 週進んで
   いた。** 自動送りが走っている間は長押しタイマーを張らないようにした
4. `PAGE_TURN_HOLD_MSEC` のコメントの理由付けが誤っていた
   （`PAGE_TURN_DOUBLE_TAP_MSEC` は「タップの間隔」、こちらは「押下時間」
   なので比べられない）。書き直した
5. `src/README.md` と `docs/User.md` に、押しっぱなしの説明を足した

## テスト

`tests/test_browser.py` に `_press_button()`（離さずに押す）と 8 件。

- `test_holding_the_button_starts_auto_page_turn`
- `test_releasing_the_button_stops_auto_page_turn`
- `test_short_tap_does_not_start_auto_page_turn`
- `test_holding_turns_the_first_week_immediately` — 500msec の時点でまず
  1 週送ることを、`AutoTurnMsec` を上限（10000）にして見る
- `test_releasing_outside_the_button_stops_auto_page_turn`（指摘 1）
- `test_holding_during_auto_page_turn_only_stops_it`（指摘 3）
- `test_moving_off_the_button_cancels_the_hold`
- `test_holding_does_not_auto_turn_in_search_mode`

- `uv run pytest tests/test_browser.py` … 85 件通過
- `uv run pytest --ignore=tests/test_browser.py` … 611 件通過
- `mise run fmt` / `lint` / `typecheck` … エラーなし
- verifier が、`main-page.js` を戻すと最初の 2 件が落ちることを確認した

### テストで踏んだこと

- **検索モードのテストが、`server` の後始末で止まった。** ボタンの上で
  指を離すと 1 週送られ、検索モードではページを読み直す。その読み直しの
  途中でテストが終わると後始末が終わらない。ボタンの外へ動かしてから
  離す形にした。1 回のテストで 12 分以上止まる
- **「ちょうど +2 週」を待つ書き方は当てにならない。** 素早い 2 回の
  タップは、週送りのアニメーションに 1 回吸われることがある。
  `test_holding_during_auto_page_turn_only_stops_it` は、自動送りが
  走っていることを「タップ 2 回では届かない週まで進んだか」で確かめてから、
  そこを基準に比べる形に書き直した

## 見送ったもの

- **負荷で落ちたときの条件付き `pytest.skip`**（reviewer 指摘 6）。
  TODO.md の懸念に書いてはいたが、実際に落ちてから入れる
- **`pageTurnPointerMoveHdr()` の `pointerId` 判定**（指摘 10）。
  `pageTurnPointerUpHdr()` も `pageTurnStart` も `pointerId` を持たない
  作りなので、既存と揃えた。直すなら別項目
- **マウスをウィンドウの外まで持っていって離したとき。** `pointerup` が
  来ないので止まらない。画面のどこかを押せば止まる

## 分担の振り返り

- **reviewer が、この項目でいちばん効いた。** テストが 80 件通ったあとで、
  実際のバグを 3 つ出した。どれも「押しっぱなしで始めた自動送りは
  ポインタに紐づく」という、ダブルタップとの前提の違いから出ている。
  テストを何件足しても、この前提の違いには気づけなかった
- **verifier は 1 回目だけ役に立った。** 「実装を戻すと新しいテストが
  落ちる」の確認は、この項目でいちばん意味のある検証だった。
  2 回目は、pytest を同時に何本も走らせて機械を詰まらせ、そのあと
  待ち続けて何も報告しなかった
- **見込みとの食い違いは、verifier の 2 回目が失敗したこと。**
  結果として、指摘への対応の確認は main が直接走らせた
- **main が料金の 72%（$10.2）を占めた。** verifier の 2 回目が失敗した
  あと、ブラウザテストの実行・失敗の切り分け・止まったプロセスの後始末を
  すべて main が抱えたため。メッセージ 80 件のうち大半がその往復で、
  reviewer（$1.5、21 件）と比べて費用対効果が悪い
- 次に同じ規模（1 ファイルへのハンドラ追加、テスト数件）をやるなら、
  **reviewer は必ず入れる**。verifier には、**テストを 1 本ずつ順に
  走らせること**と、**待つ間は何も叩かないこと**を依頼文へ明記する
  （同時実行でタイミングテストが落ち、切り分けに時間が溶ける）。
  ブラウザテストのように 5 分かかるものは、main が直接走らせたほうが
  往復が少ない
