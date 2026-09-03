# TODO-173. 月間表示でホームボタンを押しても、ゲージの針が中央に戻らない

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 20,800 / cache_creation 125,804 / 概算 $3.0 |
|      | main 93% + verifier 7%（料金の割合） |

分担を着手時に main + verifier へ変えた理由は
[archives/agents/TODO-173/README.md](../agents/TODO-173/README.md)。

## きっかけ

月間表示でホームボタンを押しても、ヘッダーのゲージの針が中央（今週、
`±0`）に戻らないことがあった。

針の位置は週間表示と同じ `setActiveWeek()`（`week.js`）が
`dispGauge(panel.dataset.monday)` で決めている。月間表示のパネルは
6 か月ブロックで、`data-monday` はそのブロックの代表日（`main_view.py`
の `base_date`）であり、ページを読み直すまで変わらない。

ホームボタンは `scrollToDate()` から `setActiveBlockOfDate()` を通り、
今日を含むブロックへ移るだけなので、**今日がすでに表示中のブロックに
入っていると、移る先が同じパネルになり、針が動かなかった**。
今日 2026-09-03 の状態で 11 月を開く（どちらも 2026-07〜12 ブロック）と、
ホームを押しても針は +11w 付近を指したままだった。

ホームボタンのときだけ `dispGauge()` を呼ぶ手もあったが、キーの `Home`
と食い違うので採らなかった。

## やったこと

`week.js` と `month.js` の 2 ファイル。

- **`setActiveWeek()` に基準日の引数 `base_date` を足した。**
  渡されたときは、パネルの `data-monday` の代わりにその日付を
  ゲージ・`activeMonday`・`#cur_day`・URL に使う。渡さなければ
  今までどおり `data-monday` を使うので、週間表示は変わらない
- **`setActiveBlockOfDate()`（`month.js`）が、受け取った日付を
  `setActiveWeek()` へそのまま渡すようにした。** ホームボタン・キーの
  `Home`・`popstate` はどれもここを通るので、まとめて「指定した日を
  指す」に揃った
- **ブロック送り（`moveActiveBlock()`）は触っていない。**
  `base_date` を渡さないので、今までどおりブロックの先頭を指す

月間表示には `date-YYYY-mm-dd` の要素が無く、`setActiveWeek()` の
`scrollToId()` は元から空振りしている。基準日を差し替えても、そこは
変わらない。

## テスト

`tests/test_browser.py` に
`test_home_button_in_month_view_moves_the_gauge_needle` を足した。
今日と同じ 6 か月ブロックの別の月（`_same_block_other_month()`）を
月間表示で開き、針が `±0` でないことを確かめてからホームボタンを押し、
`±0` になること・月間表示のまま読み直していないこと・URL が今週の
月曜になることを見る。**`week.js` と `month.js` を元へ戻すと、この
テストは針が動かずタイムアウトで落ちる**（確認済み）。

verifier の確認は
[archives/agents/TODO-173/verifier-report.md](../agents/TODO-173/verifier-report.md)。
`mise run lint` と `mise run test`（665 件）が通り、月間表示のホーム
ボタン・キーの `Home`・戻る（`popstate`）・ブロック送り・週間表示・
検索モードを、ブラウザで動かして確かめた。指摘は無し。
