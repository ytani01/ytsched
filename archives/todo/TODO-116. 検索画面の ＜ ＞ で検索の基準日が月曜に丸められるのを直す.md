# TODO-116. 検索画面の ＜ ＞ で、検索の基準日が月曜に丸められるのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 22,657 / cache_creation 148,526 / 概算 $2.5 |
|      | main 57% + implementer 34% + verifier 9%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-116](../agents/TODO-116/README.md) にある。

## きっかけ

検索画面のフッターの ＜ ＞ が使いにくい、という話から。

検索モードでは `#week_wrap` の `data-monday` が `date_from` (結果の一番
古い日) なので、`ytState.activeMonday` にも `date_from` が入る。
フッターの ＜ ＞ は一覧画面と同じ `moveToMonday()` (`week.js`) を呼び、
それをその週の月曜まで戻してから ±7 日ずらして、新しい基準日 (`date_to`)
として送っていた。表示中の期間が長いほど `date_to` が大きく戻り、
＞ を押しても先へ進まない。

ほかに、検索モードでは週パネルを 1 枚しか持たない (`main_view.py` の
`_mk_weeks()`) ため `setActiveWeek()` が必ず失敗し、週枠を滑らせる
アニメーションを見せてからページごと読み直していた (待ち時間が二重)。
ダブルタップの自動ページ送り (TODO-084) も、1 回送った時点で window
ごと作り直されて止まるので、実質効いていなかった。

## やったこと

- `main.html` の `#main` に、検索モードのときだけ
  `data-search-date-to="{{ date_to }}"` を付けた。`#week_wrap` の
  `data-monday` は `scrollToId()` などが使っているので用途を変えていない
- `main-page.js` の `pageTurnPointerUpHdr()` に検索モードの分岐を足した。
  `moveToMonday()` を呼ばず、`date_to` を ±7 日した日付で `doGet()` する。
  月曜へ丸めない
- この分岐は `moveToMonday()` を通らないので、週枠のスライドアニメーション
  も出ない
- 同じ分岐で、ダブルタップ用のタップ間隔の記録も自動ページ送りの開始も
  しない。検索モードのダブルタップはシングルタップと同じ扱いになった
- 検索画面の上部にある ＜ (`data-action="search-prev"`) は、表示中の期間ぶん
  まとめて遡る操作として今のまま残した。フッターの 1 週間ぶんとは役割が違う

## テスト

`tests/test_browser.py` に 3 件を追加。

- `test_footer_forward_button_moves_search_date_by_a_week`
- `test_footer_back_button_moves_search_date_by_a_week`
- `test_double_tap_in_search_mode_does_not_start_auto_page_turn`

`mise run lint` / `typecheck` / `test` (512 件) がすべて合格。
verifier が、`main-page.js` の検索モードの分岐を一時的に無効にすると
追加した 3 件が落ち、戻すと通ることを確認した。アプリを一時ディレクトリの
`--datadir` で起動し、テンプレートが展開されること、例外が出ないことも
確認済み。

## 残したこと

キーボードの ← → (`keyboard.js`) とスワイプ (`swipe.js`) も
`moveToMonday()` を呼んだままなので、検索モードでは同じ丸めが起きる。
今回はフッターのボタンだけを対象にしたので、直していない。

検索が過去だけをさかのぼる点は TODO-071 の担当。TODO-071 が済むと
`date_to` の意味が変わるので、そのときに ±7 日の求め方を見直す。
