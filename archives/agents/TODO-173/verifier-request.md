# TODO-173 verifier への依頼

## 目的

月間表示でホームボタンを押してもゲージの針が中央（`±0`）へ戻らない
不具合の修正が、実際に動き、既存の動きを壊していないことを確かめる。
**コードは直さない。** 見つけたことは報告する。

## 変更したファイル

- `src/ytsched/webroot/static/js/week.js`
- `src/ytsched/webroot/static/js/month.js`
- `tests/test_browser.py`

変更の中身は `git diff HEAD` で見られる（未コミット）。

## やったこと

1. `setActiveWeek(offset, push_flag, base_date)` に 3 つめの引数
   `base_date` を足した。渡されたときは、パネルの `data-monday` の
   代わりにその日付を基準日として使う（ゲージ・`activeMonday`・
   `#cur_day`・URL）。渡さなければ今までどおり
2. `setActiveBlockOfDate()`（`month.js`）が、受け取った日付を
   `setActiveWeek()` へそのまま渡すようにした
3. `tests/test_browser.py` に
   `test_home_button_in_month_view_moves_the_gauge_needle` を足した

## 完了条件

- [ ] `mise run lint` が通る（`fmt` / `fmtjs` / `typecheck` / `lintjs`）
- [ ] `mise run test` が通る
- [ ] 月間表示で、今日と同じ 6 ヶ月ブロックの別の月を開いた状態から
      ホームボタンを押すと、針が `±0` に戻る
- [ ] 同じ状態でキーの `Home` を押しても `±0` に戻る
- [ ] そのあと戻る（`popstate`）で元の日付へ戻り、針もその日を指す
- [ ] 月間表示のブロック送り（フッターの ◀▶）は、今までどおり
      ブロックの先頭を指す（針がブロック先頭の位置になる）
- [ ] 週間表示のホームボタン・週送り・ゲージのタップが今までどおり動く
- [ ] 検索モードの表示が壊れていない

## 検証のしかた

**`~/ytsched/data` を触らないこと。** 一時ディレクトリを作り、
`--datadir` に渡す。ポートは **10086** を使う（10085 は管理者が使用中）。

```sh
uv run ytsched webapp --datadir <一時ディレクトリ> --port 10086 &
```

月間表示は `?date=YYYY-MM-DD&view=month` で開く。ブロックの区切りは
1〜6 月・7〜12 月なので、**今日と同じブロックにある別の月**を開くこと
（今日が 9 月なら 2026-07-15 など）。針の位置は `#gauge_r_label` の
文字（`±0` / `+11w` など）で見るのが確実。

Playwright を直に使ってもよいし、`mise run shot` で撮って見てもよい。
撮ったら画像のパスを報告に書く。

終わったらサーバを止める（`pgrep` で PID を確かめてから kill。
`pkill` は使わない）。

## 報告

`archives/agents/TODO-173/verifier-report.md` に書く。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
