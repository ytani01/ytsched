# TODO-117. 検索画面のキーボードとスワイプも、基準日を 1 週間ぶん動かす

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 28,170 / cache_creation 268,512 / 概算 $3.5 |
|      | implementer 49% + main 41% + verifier 10%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-117](../agents/TODO-117/README.md) にある。

## きっかけ

TODO-116 でフッターの ＜ ＞ を直したが、キーボードの ← →
(`keyboard.js` の `keyHdr()`) と左右のスワイプ・ドラッグ (`swipe.js` の
`swipeFinish()`) は `moveToMonday()` を呼んだままで、検索モードでは基準日
(`date_to`) が月曜へ丸められる問題が残っていた。

## やったこと

- `week.js` の `moveToMonday()` の隣に `moveActiveDate(direction, path)` を
  足した。検索モード (`ytsched.search_date_to` がある) なら月曜へ丸めずに
  基準日を ±7 日、そうでなければ今までどおり `moveToMonday()` を呼ぶ
- フッターの ＜ ＞ (`main-page.js`)、キーの ← → (`keyboard.js`)、
  スワイプ・ドラッグ (`swipe.js`) の 3 か所から `moveActiveDate()` を呼ぶ
  形にした。TODO-116 で `main-page.js` に直接書いた日付の計算は、この
  関数へ移した
- 一覧画面の自動ページ送り (TODO-084) は `moveToMonday()` のままにした。
  検索モードでは走らないため
- **検索モードで PC のマウスの左右ドラッグが効かなかったのも直した。**
  `swipe.js` の `swipeDragTo()` は `hasAdjacentWeek()` を確かめてから
  `swipeDragging` を立てるが、検索モードでは週パネルが 1 枚しか無いので
  常に false になり、`mouseUpHdr()` がドラッグをクリックと見なして
  `swipeFinish()` へ届いていなかった (TODO-116 より前からの挙動)。検索
  モードのときだけ `hasAdjacentWeek()` の確認を見送る。追従表示
  (`translateX` とクラスの付与) は出さず、タッチと同じ挙動に揃えた。
  ドラッグと見なす距離に届かない動きは、今までどおりクリック扱い

## テスト

`tests/test_browser.py` に 6 件を追加 (合計 518 件)。

- キーボードの ← → で基準日が ±7 日動く (2 件)
- タッチのスワイプで ±7 日動く (2 件)
- マウスドラッグで ±7 日動く (1 件)
- しきい値未満のマウス操作は、今までどおり予定のクリックとして働く (1 件)

タッチのテストは `page.mouse` では再現できないので、`TouchEvent` を合成し、
`has_touch` を有効にしたコンテキスト (`page_touch` フィクスチャ) を新設した。

`mise run lint` / `typecheck` / `test` がすべて合格。implementer と
verifier の両方が、`moveActiveDate()` と `swipeDragTo()` の検索モードの
分岐をそれぞれ一時的に無効にすると対応するテストが落ち、戻すと通ることを
確認している。一覧画面 (検索していない状態) のキーボード・スワイプ・
マウスドラッグ・フッターの ＜ ＞・自動ページ送りが変わっていないことも
確認した。

## 残したこと

verifier の全体テスト実行中に `test_tap_again_stops_auto_page_turn`
(一覧画面の自動ページ送りを止めるテスト) が 1 回だけタイムアウトで落ちた。
単体では 5 回連続で通り、今回の変更は自動ページ送りの経路に触れていない
ので、全体実行時の負荷でタイミングがずれたものと見た。TODO-112 で一度
待ち方を直したテストなので、また落ちるようなら項目を立てて見直す。

検索が過去だけをさかのぼる点は TODO-071 の担当。
