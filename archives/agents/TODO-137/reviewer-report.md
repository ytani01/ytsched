# TODO-137 reviewer 報告

`git diff` と新規ファイル（`month.js` / `month.html` / `mini_cal.html`）、
`implementer-request.md` / `implementer-report.md` を読んで確認した。
コードは直していない。

## 結論

**直すべき指摘は無し。** 設計どおりに実装されており、境界の計算・状態遷移・
既存機能への影響のいずれにも問題を見つけられなかった。以下、確認した内容を書く。

## 確認したこと（問題なし）

### 1. ブロックの計算

`MainViewBuilder._mk_month_blocks()` は仕様書の「先頭月は 1 か 7」を
`block_index = (year*12+(month-1))//6` という通し月数の式で実現している。
机上で以下を追い、すべて期待どおりだった。

- 2021-06-30 → 先頭月 1（1〜6月ブロック）
- 2021-07-01 → 先頭月 7（7〜12月ブロック）
- 2021-12-31 → 先頭月 7
- 2022-01-01 → 先頭月 1
- 2026-01（offset -1）→ 2025-07（年をまたいで正しく前ブロックへ）
- 2026-12 相当（offset +1）→ 2027-01（年をまたいで正しく次ブロックへ）

`month.js` の `moveActiveBlock()` も同じ式（`total = year*12+(start_month-1)
+direction*6`）をクライアント側で独立に実装しており、同じ境界で一致する
ことを確認した。`offset` 0 の `base_date` が `args.date` そのもの、±1 が
先頭月の 1 日になっている点も設計どおり。

テスト（`tests/test_main_handler.py` の `TestMonthBlocks`）もこれらの境界
（6/30・7/1・12/31・1/1、年またぎ、3 ブロック、`base_date`）を実際に
アサートしており、「通るだけ」のテストになっていない。

### 2. 既存の週間表示・検索モード・スワイプ・自動ページ送りへの影響

- `moveActiveDate()` / `weekOffsetOfDate()` / `scrollToDate()` /
  `popstateHdr()` に足された `ytsched.view_month` の分岐は、いずれも
  関数の先頭で分けて早期 `return` しており、既存の週間表示の分岐（検索
  モードの `search_date_to` 分岐など）はそのまま残っている
- `swipeMiniCal` を立てる 2 か所（`touchStartHdr` / `mouseDownHdr`）は
  `!ytsched.view_month` を `&&` で足しただけで、週間表示での挙動
  （TODO-136 のミニカレンダー月送り）は変わらない
- 自動ページ送り（TODO-084）・フッターの ◀▶・キーの ← → は、いずれも
  `moveActiveDate()` を経由するので、月間表示ではそこ 1 か所の分岐だけで
  6 ヶ月単位になる。個別の呼び出し元を書き換える必要が無い設計どおりの作り
- `week.js` の `hasAdjacentWeek()` / `layoutWeeks()` / `setActiveWeek()` /
  `slideWeekWrap()` は `.my-week-panel[data-offset=...]` を汎用的に見て
  いるだけで、`.my-month-panel` も同じクラス・`data-offset` を持つため、
  月間表示・週間表示のどちらでもそのまま動く

### 3. モード切り替えと `elMain` の可視化

- 週⇄月の切り替えは、`doGet()`（`location.href` を書き換える実ナビゲー
  ション）を通るときだけ起きる。DOM 内だけの移動（`setActiveBlockOfDate()`
  → `setActiveWeek()`）はモードをまたがない。したがって
  `window.ytsched.view_month`（`onloadHdr()` が読み込み時に 1 回だけ
  `#main` の `data-view` から設定する値）が、ページの生存中に実際のモード
  と食い違うことは無い
- `popstateHdr()` は `pushState`/`replaceState` で積んだ同一ドキュメント内
  の履歴だけを扱うため、上と同じ理由でモードの食い違いは起きない
- 初期読み込み（`onloadHdr()`）・DOM 内移動（`setActiveBlockOfDate()` 成功
  時）のどちらも、月間表示では `ytsched.ytState.elMain.style.visibility =
  "visible"` を通る経路になっている。読み込み範囲の外（offset ±1 の外）へ
  出たときは `doGet()` で読み直され、そこでまた `onloadHdr()` が走るので、
  白いままになる経路は見つからなかった

### 4. 見た目・プロジェクトの決まり

- `my.css` に足したのは `.my-month-title` / `.my-month-grid` /
  `.my-month-grid .my-mini-cal` の 3 つだけで、色・大きさの値は既存の
  ミニカレンダーのスタイルをそのまま使っている（新しい色や大きさは
  作っていない）
- `mini_cal.html` の切り出しは `sde.html` と同じ「呼び出し側が
  `{% set %}` してから `{% include %}` する」流儀に揃えてあり、必要な
  変数（5 個）がファイル先頭のコメントに列挙されている
- コメントは「なぜそうしたか」を書き、TODO-137 で参照する周りの書き方に
  揃っている
- `docs/User.md` に TODO 番号は書かれていない（`src/README.md` /
  `tests/README.md` には TODO-137 の参照があり、これは開発者向け文書
  なので問題無い）
- `ruff check` を該当の Python 3 ファイル（`main_binder.py` /
  `main_view.py` / `sched_load.py`）に対して実行し、通ることを確認した

### 5. テストの実質性

- `tests/test_web.py` の `TestMonthView` は、検索モードでの上書き・不正な
  `view` の既定値落ち・ブロック数・caption の月数を、実際の HTML から
  正規表現で抜き出してアサートしている
- `tests/test_browser.py` の `test_month_view_round_trip` は、週間表示の
  `YYYY/MM` を実際にクリックして月間表示へ移り、日付セルをクリックして
  週間表示へ戻ることを、URL とスクロール先の要素の両方で確認している

## 確信度の低い所見（直す必要は無いと考えるが、念のため書く）

- 月間表示でもヘッダーの横ゲージ（`dispGauge()`）が週間表示と同じ計算
  （`activeMonday` からの週・月・年差）で出る。月間表示の「基準日」は
  ブロックの先頭月の 1 日や `args.date` であり、必ずしも月曜ではないが、
  `mondayOf()` がその週の月曜に丸めてから差を計算するので、表示自体は
  壊れない。仕様は「ヘッダー・フッターは週間表示と同じものを出す」と
  明記しているので、これは仕様どおりの動きだと理解しており、指摘とい
  うより確認事項として書く
