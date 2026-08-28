# TODO-097 implementer 報告

## やったこと

対象 9 ファイルの先頭（既存の `/** (c) ... */` と `// 〜 (TODO-0xx)` の 1 行説明の直後）に、
「外へ出すもの」「外から使うもの」を並べた `//` コメントを追加した。挙動の変更はなし。

依存は grep で洗い出した（`static/js/` 全体と `templates/` を横断）。判定は「実際の関数呼び出し・
属性ハンドラ」のみを採用し、HTML コメントや JS コメント内の言及は除外した。

## 変更ファイル（すべてコメント追加のみ）

- `src/ytsched/webroot/static/js/state.js` — provides: `ytState`。depends: なし
- `src/ytsched/webroot/static/js/spinner.js` — provides: `loadingSpinner()`（+ `pageshow` 登録）。
  depends: `ytState`(state)
- `src/ytsched/webroot/static/js/gauge.js` — provides: `mondayOf` `dispGauge` `dispGaugeMarks`
  `gaugeBarClickHdr`(main.html)。depends: `shiftDays` `getLocaltimeDateString` `calcDays`
  `scrollToDate`(nav)、`ytState`(state)
- `src/ytsched/webroot/static/js/nav.js` — provides: `shiftDays` `getLocaltimeString`
  `getLocaltimeDateString` `calcDays` `doGet` `doPost` `doSubmit` `doGetDate` `scrollToId`
  `scrollToDate` `pushDateInUrl` `popstateHdr`。depends: `ytState`(state)、`loadingSpinner`(spinner)、
  `weekOffsetOfDate` `setActiveWeek`(week)
- `src/ytsched/webroot/static/js/week.js` — provides: `weekOffsetOfDate` `hasAdjacentWeek`
  `layoutWeeks` `setActiveWeek` `slideWeekWrap` `moveToMonday`。depends: `ytState`(state)、
  `mondayOf` `dispGauge`(gauge)、`getLocaltimeDateString` `getLocaltimeString` `shiftDays`
  `pushDateInUrl` `scrollToId` `doGet`(nav)
- `src/ytsched/webroot/static/js/keyboard.js` — provides: `keyHdr`（main-page.js が keydown 登録）、
  `followKeyboard`（自前で登録）。depends: `moveToMonday`(week)、`getLocaltimeDateString`
  `scrollToDate`(nav)、`url_prefix`(base.html)
- `src/ytsched/webroot/static/js/swipe.js` — provides: `touch*Hdr` / `mouse*Hdr` の 7 ハンドラ
  （main-page.js が登録）。depends: `ytState`(state)、`slideWeekWrap` `hasAdjacentWeek`
  `moveToMonday`(week)、`url_prefix`(base.html)
- `src/ytsched/webroot/static/js/main-page.js` — provides: `homeButtonHdr` `changeSearchN`(main.html)、
  末尾で各ハンドラを window に登録。depends: `search_str0` `today_str` `auto_turn_msec`(main.html)、
  `url_prefix`(base.html)、`ytState`(state)、`loadingSpinner`(spinner)、`doGet` `doPost`
  `scrollToDate` `popstateHdr`(nav)、`layoutWeeks` `moveToMonday`(week)、`dispGauge` `dispGaugeMarks`
  (gauge)、`keyHdr`(keyboard)、swipe.js の 7 ハンドラ
- `src/ytsched/webroot/static/js/edit-page.js` — provides: `submitCmd` `update_wday` `setElDate`
  `changeElDate`(edit.html)、`changeDetailHeight` `onloadEdit`（自前で登録）。depends: `ytState`
  (state)、`loadingSpinner`(spinner)

## 作成ファイル

- `archives/agents/TODO-097/implementer-report.md`（本ファイル）

## TODO.md の代表表になかった依存（想定と違ったもの）

- `gauge.js` → `nav.js` の `scrollToDate()`（`gaugeBarClickHdr` 内）。表は `shiftDays` /
  `calcDays` / `getLocaltimeDateString` の 3 つだけ挙げていた。
- `week.js` → `nav.js` の `getLocaltimeDateString` / `getLocaltimeString` / `shiftDays` /
  `pushDateInUrl` / `doGet`。表は `mondayOf` / `dispGauge`(gauge) と `scrollToId`(nav) のみ。
- `swipe.js` → `week.js` の `hasAdjacentWeek()`、`state.js` の `ytState`。表は `url_prefix` と
  `moveToMonday` / `slideWeekWrap` のみ。
- 読み込み順（base.html）は state → spinner → gauge → nav → week → keyboard → swipe だが、
  gauge/nav/week は「あとに読み込まれるファイル」の関数を呼ぶ。実行時にしか呼ばれないので前方
  参照でよい、という点を該当 3 ファイルのコメントに 1 行添えた（この項目の主旨そのもの）。

## 判断したこと

- **depends on の粒度**: DOM 要素 id（`loadingSpinner` など）は「テンプレート由来の名前」だが、
  TODO 本文が例示するのは `<script>` 内の定数（`url_prefix` / `search_str0` / `today_str` /
  `auto_turn_msec`）なので、depends on にはそれらと他 `.js` のトップレベル名だけを挙げ、DOM id は
  除外した。全ファイルが多数の id を触るため、挙げると冗長になり主旨がぼやける。
- **コメントのスタイル**: 既存の `swipe.js` 冒頭（`// swipeStart / swipeDragging / ... は、` と
  バッククォート無しで名前を並べる）を前例とし、`//` 行コメント・バッククォート無し・関数は `()`
  付きで統一した。枠線・ASCII アートは無し。
- `keyboard.js` の `keyHdr` 内 `const today_str` は関数ローカルで main.html の `today_str` とは
  別物。紛らわしいので 1 行注記した。

## 確認したこと

- `mise run fmt`: ruff format / check とも変更なしで通過。
- `mise run lint`: ESLint（lintjs）通過、指摘なし。typecheck（basedpyright / mypy）も 0 件。
- `mise run test`: 480 passed / 1 failed。失敗は `tests/test_browser.py::test_tap_again_stops_auto_page_turn`。
  `git stash` してクリーンな作業ツリーでも同じ内容で失敗する（`assert '2026-09-21' == '2026-09-14'`）
  ことを確認済み。自動ページ送りの待ち時間に依存するテストで、今回のコメント追加とは無関係の
  既存の失敗。TODO-084 の範囲。

## 残した気づき（直していない）

- 上記のブラウザテスト 1 件の失敗は TODO-097 の範囲外なので手を付けていない（TODO-084 の範囲）。
