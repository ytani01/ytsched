# TODO-097 verifier report

対象: `src/ytsched/webroot/static/js/` の 9 ファイル先頭コメント追加（挙動変更なし）。

## 1. 記述の正確さ

grep で全項目を裏取りした。**provides / depends on の向き・関数の帰属・
「このファイル内だけ」の判定は、すべて正しい。挙げ漏れ・誤りは無し。**

確認したこと:
- 各 provides の関数が、他 `.js` かテンプレートから実際に参照されている
  （`mondayOf` `dispGauge` `dispGaugeMarks` `gaugeBarClickHdr` `shiftDays`
  `getLocaltimeString` `getLocaltimeDateString` `calcDays` `doGet` `doPost`
  `doSubmit` `doGetDate` `scrollToId` `scrollToDate` `pushDateInUrl`
  `popstateHdr` `weekOffsetOfDate` `hasAdjacentWeek` `layoutWeeks`
  `setActiveWeek` `slideWeekWrap` `moveToMonday` `keyHdr` `loadingSpinner`
  `ytState` `homeButtonHdr` `changeSearchN` `submitCmd` `update_wday`
  `setElDate` `changeElDate` すべて追跡）
- 「このファイル内だけで使う」と書かれた名前（`days2xPercent` `xPercent2days`
  `GAUGE_MARKS` `gaugeDiffLabel` `setGaugePosition` `GAUGE_MONDAY_KEY`
  `get/setGaugeMonday` `placeGaugeWithoutTransition` `DAYS_*` `mkUrl`
  `replaceDateInUrl` `weekPanelOf` `cancelActiveSlide` `SWIPE_SLIDE_MSEC`
  `isTyping` `followKeyboard` `SWIPE_*` `MOUSE_AFTER_TOUCH_MSEC`
  ページ送り系ハンドラ `mkInput` `wdayList` `busyFlag`）は、
  いずれも他ファイル・テンプレートから参照が無いことを確認
- 4 つのテンプレート定数: `url_prefix` は swipe/keyboard/main-page が使用、
  `search_str0` `today_str` `auto_turn_msec` は main-page が使用。
  コメントの記載と一致。gauge.js / nav.js は `url_prefix` を使っておらず、
  コメントでも挙げていない（正しい）
- main-page.js が swipe.js の 7 ハンドラ（touch 4 + mouse 3）を
  `addEventListener` している（`main-page.js:263-274`）ことを確認
- keyboard.js の「`keyHdr` 内の `today_str` はローカル変数で main.html の
  ものとは別物」（`keyboard.js:111`）は正しい指摘
- spinner.js の `pageshow` リスナー、keyboard.js の `followKeyboard` を
  visualViewport/window に登録、も確認

### 細かい不正確さ（誤りではない。締めるかは main 判断）

1. **nav.js**: `doGet() / doPost() / doSubmit() / doGetDate()` を
   「main.html・sde.html・edit.html の onmousedown / onchange」と一括りに
   しているが、sde.html と edit.html から呼ばれるのは `doGet` だけ
   （`sde.html:86` / `edit.html:35`）。`doPost`（`main.html:186`）・
   `doSubmit`（`main.html:297,351,372`）・`doGetDate`（`main.html:89,112`）は
   main.html だけ。4 関数すべてが 3 テンプレートに出るように読める。
2. **nav.js**: `shiftDays / getLocaltimeString / getLocaltimeDateString /
   calcDays` を「gauge.js・week.js・keyboard.js の日付計算から」と一括り。
   実際は `getLocaltimeString` は week.js のみ（`week.js:244`）、
   `calcDays` は gauge.js のみ（`gauge.js:176`）。過大な近似。
3. **gauge.js**: 「外から使うもの（すべて nav.js …）」の見出しの下に
   `ytState (state.js)` が並ぶ。行自体に `(state.js)` と注記はあるが、
   「すべて nav.js」と食い違う。
4. **edit-page.js**: 「`changeDetailHeight()` / `onloadEdit()` は window の
   load でこのファイルが登録し」。`onloadEdit` は直接登録
   （`edit-page.js:99`）だが、`changeDetailHeight` は無名の load ハンドラ内
   から呼ばれるだけ（`edit-page.js:96-98`）で、それ自体は登録していない。
   実行タイミングは load で正しく、表現がやや緩いだけ。

## 2. 挙動が変わっていないこと

`git diff` は 122 行の追加のみ・削除ゼロ。追加行はすべて `//` コメント。
コードには一切手が入っていない。○

## 3. fmt / lint

- `mise run fmt` ○（ruff format: 31 files unchanged / ruff check: All checks passed）
- `mise run lint` ○（eslint クリーン、basedpyright 0 errors、mypy Success）

## 4. test（`mise run test`）

- 1 回目（変更あり）: **1 failed, 480 passed**。落ちたのは
  `tests/test_browser.py::test_tap_again_stops_auto_page_turn`
  （`AssertionError: assert '2026-09-21' == '2026-09-14'`）。
- `git stash`（stash 前 `git status` 確認済み・9 ファイルのみ、pop 済み）で
  クリーンな作業ツリーにして検証:
  - 当該テスト単体: **passed**
  - 全体（`mise run test`）: **481 passed**
- `git stash pop` 後、変更ありで全体を再実行: **481 passed**

→ この失敗は**タイミング依存の flaky**（auto page turn 300ms + 待ち時間の
Playwright テスト）で、コメントのみの変更とは無関係。ただし実装者が言う
「クリーンな作業ツリーでも決定的に失敗する既存の失敗（TODO-084 範囲）」は
**再現しなかった**（クリーンでは通った）。断続的な失敗。

## 判断が要る点

- 細かい不正確さ 1〜4 を修正させるか、このままにするか（いずれも
  依存の向き・load 順の要点は誤っていない）。
- flaky な `test_tap_again_stops_auto_page_turn` の扱い（本項目の範囲外だが、
  実装者の認識と実際の挙動がずれている）。
