# TODO-213. 更新した日付と予定を点滅させる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |
| 実施 | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Sonnet 5.5 / medium） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 116 | 25,329 | 140,395 | 4,202,841 | 50% |
| reviewer | Opus 5.5 | high | 76 | 3,823 | 87,505 | 2,206,428 | 26% |
| implementer | Sonnet 5.5 | medium | 62 | 1,078 | 97,604 | 1,233,626 | 15% |
| verifier | Sonnet 5.5 | medium | 48 | 494 | 44,847 | 777,485 | 9% |
| 合計 |  |  | 302 | 30,724 | 370,351 | 8,420,380 | 計 8,821,757 |

- モデル・effort はどの担当も定義のまま（上書きなし）
- 集計は決着のコミット前の時点まで

## きっかけ

追加・修正・削除で一覧へ戻ったとき、どこが変わったのかが分かりにくい。
更新した日付と予定を、戻った直後に点滅させて示す。

## やったこと

- `src/ytsched/main_handler.py`: `exec_cmd()` が点滅させる `sde_id` も返し、
  `post()` が一覧へ戻すリダイレクトに `flash_date` / `flash_sde_id` を足す。
  削除は日付だけ。`update`（編集画面へ戻る）と cmd の無い POST には足さない
- `src/ytsched/webroot/static/js/main-page.js`: `flashUpdated()` が `load` で
  クエリを読み、日付の欄（`#date-… .my-date-col`）と予定の行
  （`data-sde-id` の要素から `closest(".my-sde")`）に `my-flash` を付ける。
  付けたあと `history.replaceState` で `flash_*` だけ URL から消す。
  `animationend` と `animationcancel` で class を外す
- `src/ytsched/webroot/static/css/my.css`: `.my-flash` と `@keyframes my-flash`
  （3 秒で 3 回）。背景色ではなく `box-shadow: inset` で黄色を重ねる
- `src/README.md`: POST-Redirect-GET の段落に 2 行
- テスト: `tests/test_web.py` にリダイレクトのクエリ（add / fix / del / cmd 無し）、
  `tests/test_browser.py` に class の付き方・URL の掃除・class の外れ方

reviewer の指摘で、最初の実装から次を直した。

- 日付の行（`#date-…`）の背景は中の欄に覆われ、黄色が 0.26% しか見えなかった
  → 日付の欄に付ける
- 背景色を `transparent` にする相で、元の背景色（休日・ToDo）が消えて地の色が
  見えた → `box-shadow: inset` にする
- class が残り、週を移って戻ると点滅し直した → `animationend` /
  `animationcancel` で外す

## 確かめたこと

- `mise run lint` / `mise run test` が通る（718 passed）
- 実機で、追加・日付を変えた修正・削除・update・再読み込み・点滅の途中で週を
  2 週移って戻る、を 1 回ずつ（`archives/agents/TODO-213/verifier-report.md`）。
  点滅の相の黄色は、日付の欄で 62〜65%、予定の行で 83〜85% の画素
- テストは、`closest`・`replaceState`・`classList.remove` を外すと落ちる

## 残ること

- `box-shadow` での点滅はテストで守られていない（`background-color` に戻しても
  テストは通る）。見た目だけの話なので足していない
- `cmd=add`（既存の予定の複製）は実機では試していない。リダイレクトのクエリは
  `tests/test_web.py` で見ていて、JS 側は fix と同じ道を通る
- 点滅の途中で 1 週だけ移って戻ると、点滅の続きが見える可能性がある（未測定）

## 分担の振り返り

- implementer は要件どおり実装したが、`data-sde-id` が内容欄にあることを
  「判断が要る点」として返し、点滅が実際に見えるかは測らなかった。reviewer が
  実測で 3 件（日付の欄が覆われる、元の背景色が消える、class が残る）と、
  再確認で `animationcancel` の件を見つけた。verifier は食い違いを見つけなかった
- 見込みどおりの編成で動いた。食い違ったのは巡回の数で、見た目の項目なのに
  最初の依頼に「点滅の相の画素を測る」を入れなかったため、reviewer の実測で
  1 巡増えた
- 次に見た目の変わる項目を組むときは、implementer の完了条件に
  「スクリーンショットで、その色が実際に見えるかを測る」を入れる。
  reviewer は見た目の実測より、分岐とイベントの漏れに絞れる
