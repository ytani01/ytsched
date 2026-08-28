# TODO-103 verifier 報告

依頼書（`archives/agents/TODO-103/verifier-request.md`）の通り確かめた。

## 1. lint / typecheck / pytest

- `mise run lint` ○（ruff format / check、eslint すべて緑）
- `mise run typecheck` ○（basedpyright: 0 errors、mypy: no issues）
- `uv run pytest -q` 490 件成功、1 件失敗
  （`test_browser.py::test_tap_again_stops_auto_page_turn`）。
  `git stash -u` で今回の変更を外した状態で同じテストを 4 回走らせたところ、
  そのうち 1 回失敗した。**この変更が原因ではない既存の flaky テスト**と確認できた。

## 2. アプリの起動と画面での確認

一時ディレクトリに `-3, -1, 0, 2, 5, 10, 35, -35` 日分の予定データを
自作して置き、`ytsched webapp --datadir <一時ディレクトリ> --port 10085`
で起動（既定ポートで `tools/screenshot.py` に合わせた）。

- ○ 週間表示の日曜日の下に、2 ヶ月分のミニカレンダーが横に並ぶ
- ○ 出ている月は「表示中の週の月曜が含まれる月」と「その翌月」
  （例: 週 2026-08-24〜が月曜のとき `2026/08` と `2026/09`）
- ○ 予定がある日に `.my-mini-cal-dot` が出て、無い日には出ない
- ○ 日付タップ（範囲内 `2026-08-26`）: `scrollToDate` がスクロールのみで
  処理し、URL は `date=2026-08-26` に置き換わる。ページ再読込は無い
- ○ 日付タップ（範囲外 `2026-09-30`、ロード済み週の外）:
  `scrollToId` が要素を見つけられず `doGet()` に落ち、
  `location.href` が `?date=2026-09-30&sde_align=top` に変わって
  ページが再読込された
- ○ 前後の月の埋めセル（`.my-mini-cal-day-out`、16 個検出）はタップしても
  URL・状態とも変化なし
- ○ 今日は青枠（`.my-mini-cal-day-today`）、表示中の週の 7 日は
  黄色背景（`.my-mini-cal-day-cur-week`）で見分けられる
- ○ 週送り（forward ボタン 5 回）で月をまたぎ、`2026/08〜2026/09` から
  `2026/09〜2026/10` に正しく切り替わった（`moveToMonday` のログで確認）
- ○ 検索したとき（`search_str` を設定して検索）は `.my-mini-cal` が
  0 個（出ない）
- ○ 幅 412px で `document.documentElement.scrollWidth` と
  `clientWidth` がともに 412 で、横スクロールは出ない
- ○ 取得した HTML に `{{` `{%` の生残りなし、`my-mini-cal-caption` /
  `my-mini-cal-dot` とも正しく展開されている
- ○ サーバログ（起動〜一連の操作後）に例外・トレースバックなし

スクリーンショット: `/home/ytani/tmp/playwright-mcp/todo103week_closed_412.png`
（8月24日〜30日の週。今日 8/29 が青枠、週の 7 日が黄色背景、
2026/08 と 2026/09 のミニカレンダーが横に並び、ドットも出ている）

## 見つけたこと（軽微）

なし。依頼書に書かれた確認項目はすべて期待通りに動いた。

## 判断が要る点

なし。

## 追加確認（reviewer 指摘の修正後）

`SchedData.sdf_has_sde()` の新設と `load_month_cal()` の `has_sched` 切り替えを確認した。

### 1. lint / typecheck / pytest

- `mise run lint` ○（ruff format / check、eslint すべて緑）
- `mise run typecheck` ○（basedpyright: 0 errors、mypy: no issues）
- `uv run pytest -q` 494 件成功、1 件失敗
  （`test_browser.py::test_tap_again_stops_auto_page_turn`）。
  前回の確認で `git stash` により**この変更と無関係の既存 flaky
  テスト**と確認済みのものと同一テスト。新規テスト 4 本
  （`test_sdf_has_sde*` 3 本、`test_has_sched_ignores_empty_file`）を
  含めて通過している

### 2. アプリでの確認（一時 datadir、今日 2026-08-29 に 1 件の予定を用意）

- ○ 予定がある日（今日）に `.my-mini-cal-dot` が出る（削除前は
  ミニカレンダー内に 6 個検出）
- ○ 編集画面相当の POST（`cmd=del`、`orig_date`/`date`/`sde_id` を
  指定）で予定を削除。ファイルは `wc -c` で 0 バイトのまま残ることを
  確認（`sdf_exists()` だけでは消えない状態を再現できた）
- ○ 削除後に同じ日を GET し直すと `.my-mini-cal-dot` が 0 個
  （消えている）
- サーバログに例外・トレースバックなし

### 3. 他の項目への影響

- ○ 月の組み合わせ: 削除後も検索解除後の HTML で各週パネルにつき
  隣接する 2 ヶ月分のキャプション（例: `2026/08`→`2026/09`）が並んでいる
- ○ 検索モード: `search_str=delete-me` を POST したあとの GET で
  `.my-mini-cal` が 0 個（出ない）。検索解除で復帰することも確認
- タップ（範囲内/範囲外・埋めセル）は今回のサーバ側の変更（ドットの
  出し方のみ）と無関係なため、コードの読み直しのみで再確認は省いた
  （テンプレート・JS 側は無変更）

見つけたことは無い。判断が要る点も無い。
