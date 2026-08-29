# TODO-105. ホームボタンで今週の月曜日へ移動する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier + wording |
| 実施 | Opus 5 / effort high | main のみ |

（トークンの残りが少なくなったため、verifier は読み込み順の確認だけで
打ち切り、lint・テストは main が走らせた。wording は立てていない。
消費の集計も省いた。）

## きっかけ

ホームボタンを押したときの移動先が今日だった。週間表示では週の頭が
見えているほうが分かりやすいので、シングルクリックもダブルクリックも
今週の月曜日へ移動するようにしたい。

## やったこと

- `main-page.js` の `homeButtonHdr()` の先頭で
  `const monday_str = getLocaltimeDateString(mondayOf(today_str));` を求め、
  シングル側の `doPost` の `date`・`scrollToDate` の日付と、ダブル側の
  `doGet` の `date` を、`today_str` からこれに差し替えた
- `mondayOf()` は `gauge.js`、`getLocaltimeDateString()` は `nav.js` にある。
  どちらも `base.html` で `main-page.js` より先に読まれるので、そのまま呼べる
- 呼び出し関係を先頭コメントに書く決まり（TODO-097）に合わせて、
  `main-page.js`・`nav.js`・`gauge.js` のコメントも直した
- ボタンの表示（`main.html` の `my-home-date`）は今日の日付のままにした。
  「今日がいつか」を出す場所なので、移動先とは別
- キーボードの Home キー（`keyboard.js`）も今日へ移動したままにした

## テスト

- `tests/test_browser.py::test_home_button_moves_the_view` の期待値を、
  URL が今日になることから、今週の月曜になることへ変えた。今日の欄が
  実際に画面へ出ることを見る部分（TODO-049 で入れたもの）はそのまま
- `mise run lint` は通った。`mise run test` は
  `test_tap_again_stops_auto_page_turn` だけが落ちるが、**この変更を
  外した状態でも同じように落ちる**（`git stash` して 2 回走らせて確認）。
  自動ページ送りの停止を待ち時間で見るテストで、元から不安定。
  今回の変更とは関係しない。別項目として立てるかどうかは未定
