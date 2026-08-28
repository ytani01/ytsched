# TODO-093. 表示中の週の月曜日の日付を DOM から `ytState` へ移す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer + verifier + wording |
| 消費 | output 29,930 / cache_creation 352,305 / 概算 $2.5 |
|      | main 64% + implementer 27% + verifier 8% + wording 1%（料金の割合） |

基本設計のレビュー（2026-08-27）の M。TODO-083（ファイルをまたぐ状態は
`ytState` に集める）の積み残し。

## きっかけ

週表示は DOM の中だけで週を移る（TODO-069）ので、どの週を見ているかを
ブラウザ側で覚えておく必要がある。その値（表示中の週の月曜日、
`YYYY-MM-DD` の文字列）が `#cur_day` / `#date` / `#date_from` の 3 か所に
分かれて入っていた。`setActiveWeek()`（`week.js`）が週を移るたびに 3 つ
とも書き換えて揃え、読むほうは `moveToMonday()` が `#cur_day`、
`onloadHdr()` が `#date_from` を見ていた。

## やったこと

- `state.js`: `ytState` に `activeMonday`（`YYYY-MM-DD` 文字列）を足した。
- `main.html`: `#date_from` の hidden input を消し、`#week_wrap` に
  `data-monday="{{ date_from }}"` を付けた。サーバから渡ってくる初期値は
  ここだけに残す。`#cur_day`・`#date` の input はそのまま。
- `main-page.js`: `onloadHdr()` で `#week_wrap` の `data-monday` から
  `ytState.activeMonday` を一度だけ入れる。以後は `dispGauge()` も
  `changeSearchN()` も `ytState.activeMonday` を読む。
- `week.js`: `setActiveWeek()` は `ytState.activeMonday` と、画面に出て
  いる `#date` の value を揃える（`#cur_day` / `#date_from` のループは
  やめた）。`moveToMonday()` は `ytState.activeMonday` から日付を作る。
- `nav.js`: `#cur_day` は `doSubmit()` がフォーム送信の直前に
  `ytState.activeMonday` を載せる（送るときだけ書く）。`popstateHdr()`
  と `scrollToDate()` は `#cur_day` の読み書きを `ytState.activeMonday`
  に置き換えた。

読み込み直後、これまでは `#cur_day` が基準日（`date`）で、週を 1 回
移ると月曜に変わっていた。今回の一本化で、初回から
`ytState.activeMonday` は月曜になる。`cur_day` はサーバ側で `date` が
無いときの弱い手がかりで、数日ずれても検索結果はほぼ変わらないので、
そのままにした（TODO 本文でも承知していた差）。

## テスト

- `mise run fmt` / `fmtjs` / `lint` / `lintjs` / `typecheck`: 緑。
- `mise run test`: 481 passed。
- `tests/test_browser.py`: 22 passed。`test_tap_again_stops_auto_page_turn`
  が実行のたびに落ちたり通ったりするが、TODO-093 を外したクリーンな
  `develop` でも同じ assert で落ちるので、既存の flaky（TODO-084 の
  自動ページ送りの停止タイミング）で、今回の変更由来ではない。
- `tests/test_main_handler.py`: `#date_from` の hidden の `value="..."` を
  見ていた 4 件を `data-monday="..."` に直した（1 件は hidden 削除で
  実際に落ち、3 件は `#date` の value と偶然一致して緑のままだったが、
  `date_from` を見る意図に揃えた）。
- 一時 datadir でアプリを起動し、`#week_wrap` に `data-monday` が付き
  `id="date_from"` が消えていることを curl で確認。
