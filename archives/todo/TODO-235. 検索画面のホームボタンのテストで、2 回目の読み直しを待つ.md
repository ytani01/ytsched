# TODO-235. 検索画面のホームボタンのテストで、2 回目の読み直しを待つ

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 54 | 9,536 | 79,661 | 1,662,257 | 76% |
| impl-235（implementer） | Sonnet 5.5 | medium | 20 | 4,313 | 33,209 | 288,044 | 14% |
| verify-235（verifier） | Sonnet 5.5 | medium | 16 | 2,592 | 25,041 | 192,031 | 10% |
| 合計 |  |  | 90 | 16,441 | 137,911 | 2,142,332 | 計 2,296,774 |

## きっかけ

TODO-234 で、ホームボタンが今日を日付に指定するようになった。検索画面では
1 回目の読み直しで URL が `date=<今日>` になり、待ち合わせの目印（`_mark`）も
1 回目で消える。2 回目の読み直し（検索を抜けた画面）を待たずに判定へ進む
おそれがあった。

## やったこと

- `tests/test_browser.py` の `_wait_for_top_screen()` で、URL を待ったあとに
  `#main:not([data-search-date-to])`（検索モードが解けた）も待つようにした。
  依頼では `_mark` / `_wait_for_reload` を使い回す指定だったが、目印は 1 回目で
  消えるので 2 回目は待てない。検索モードの有無で待つ形にした。
  週間・月間表示から呼ぶテストでは、もともと検索モードでないので即座に通る
- アプリ側のコードは変えていない
- 2 つ目の「検索画面の 1 回目のタップ後の点滅テストを足すか」は、利用者が
  **足さない**と決めた。点滅は TODO-234 で通常画面のテストがある

## 確かめたこと

詳細は `archives/agents/TODO-235/` の報告。

- `_wait_for_top_screen` の呼び出し元のテスト 7 件が通る
- `main-page.js` の検索画面の分岐で `reloadHome()` を外すと、検索画面の
  ダブルタップのテストが落ちる（implementer）
- 足した条件だけを外すと、同じテストが `_assert_top_screen` の
  「検索モードが解けていない」で落ちる（verifier）。修正前は誤って通るのでなく、
  機械の速さ次第で落ちうる形だった。実際に落ちる場面は再現していない
- `mise run lint` / `mise run typecheck` が通る

## 分担の振り返り

- implementer は、依頼の「`_wait_for_reload` を使い回す」が成り立たないことを
  見つけ、別の待ち方にした。verifier は、足した条件が効いていることを、
  条件を外した版で落として示した。どちらも食い違いの指摘は無い
- 見込みとの食い違いは無い。`model-check.md` も 2 件とも「見合う」
- 次に同じ規模（テストの待ち合わせを 1 か所直す）なら、同じ組み方でよい。
  依頼に使う関数を名指しする前に、その関数が今の挙動で使えるかを main が
  1 回読んでおけば、implementer の回り道が減る
