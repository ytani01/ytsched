# TODO-129 verifier 報告

## 1. テストと lint

- `mise run test` — 552 件 pass（131.86s）。例外なし
- `mise run lint`（fmt / typecheck / lint 一式）— fmt・ruff check・basedpyright
  （0 errors）・mypy（no issues, 35 files）・eslint すべて通過

## 2. テストデータと画面

一時ディレクトリ
`/tmp/claude-649/.../scratchpad/ytsched-data-129` に 2026年8月のデータを作成:

| 日付 | 内容 |
|---|---|
| 8/4（火） | ふつうの予定だけ |
| 8/5（水） | 重要な予定（`!重要な会議`） |
| 8/6（木） | 取り消し済みの予定だけ（`(欠)中止になった会議`） |
| 8/7（金） | `type: 祝日` の予定（平日） |
| 8/11（火） | ToDo 締切だけ |
| 8/12（水） | ToDo 締切 ＋ ふつうの予定 |
| 8/13（木） | 予定なし |

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 10199` を起動し、
`curl http://localhost:10199/ytsched/?date=2026-08-19` が 200 を返すことを確認。
`mise run shot -- --open -p todo129 'http://localhost:10199/ytsched/?date=2026-08-19'`
で撮影。使い終わったプロセスは `pgrep -f` で PID を確認して kill 済み。

撮った画像:

- `/home/ytani/tmp/playwright-mcp/todo129_closed_412.png`
- `/home/ytani/tmp/playwright-mcp/todo129_open_412.png`
- `/home/ytani/tmp/playwright-mcp/todo129_closed_800.png`
- `/home/ytani/tmp/playwright-mcp/todo129_open_800.png`
- `/home/ytani/tmp/playwright-mcp/todo129_minical_crop_412.png`
  （412px 版のミニカレンダー部分だけを 4 倍に拡大したもの。目視確認用）

## 3. 見た目の確認（○）

拡大画像（`todo129_minical_crop_412.png`）で確認。

- 背景色の優先度: 8/2（日）・8/9（日）・8/16（日）・8/23（日）・8/30（日）が
  濃いピンク、8/1・8/8・8/15・8/22・8/29（土）が薄いピンク、8/7（金・祝日）も
  濃いピンクになり、**祝日が曜日の色より優先**されている。表示中の週
  （8/17〜8/21、`?date=2026-08-19` の月〜金）は白、8/22・8/23（同じ週の
  土日）は白ではなくピンクのままで、**週の白より祝日・週末が優先**されている。
  それ以外の週（8/3・8/10・8/24〜8/28 など）は薄いグレー。表の優先度どおり
- 8/5（重要な予定のみ）は赤いドット。8/4（ふつうの予定）・8/6（取り消し済み
  のみ）は青いドットで、**取り消し済みだけの日は赤くならない**ことを確認
- 8/11（ToDo 締切のみ）は四角だけ。8/12（ToDo ＋ ふつうの予定）はドットと
  四角が横に並んで両方出ている
- 24px のセルから丸・四角がはみ出す様子は無く、拡大画像でも丸と四角は
  見分けられる
- 表示中の週が白になったことで、今週がどこかは一見しただけでは分かりにくい
  （グレーの他の週との差は淡く、拡大しないと気づきにくい）。ただし今日の日付
  （8/31）には別途青い枠が付いており、それと合わせて見ればどこが今日か・
  今週かは判別できる

## 判断が要る点

- 「表示中の週が白」は薄いグレーとの差が小さく、パッと見て今週の位置が
  分かりにくい（TODO.md の残る懸念どおり）。色の濃さを調整するかどうかは
  main の判断

## 追加確認（グレーの濃さ）

- `mise run test` — 553 件 pass（128.51s）。追加された
  `test_todo_in_day_file_is_shown_as_todo` を含めて全て通過。例外なし
- 同じテストデータ・同じ URL（`?date=2026-08-19`）で撮り直し。ポート
  10198 で起動し `curl` で 200 を確認、`mise run shot -- --open -p todo129b`
  で撮影。使用後は `pgrep -af` で PID を確認して kill 済み

撮った画像:

- `/home/ytani/tmp/playwright-mcp/todo129b_closed_412.png`
- `/home/ytani/tmp/playwright-mcp/todo129b_open_412.png`
- `/home/ytani/tmp/playwright-mcp/todo129b_closed_800.png`
- `/home/ytani/tmp/playwright-mcp/todo129b_open_800.png`
- `/home/ytani/tmp/playwright-mcp/todo129b_minical_crop_412.png`
  （ミニカレンダー部分だけを 4 倍に拡大したもの）

`todo129_minical_crop_412.png`（変更前）と `todo129b_minical_crop_412.png`
（変更後）を見比べた。

- グレー（`#E4E4E4`）が前より濃くなり、**表示中の週（8/17〜8/21、白）との
  差がはっきり付いた**。前回の懸念（今週の位置が分かりにくい）は解消して
  いる
- 土日（8/1・8/8・8/15・8/22・8/29 の薄いピンク、8/2・8/9・8/16・8/23・
  8/30 の濃いピンク）・祝日（8/7）の色、8/5 の赤ドット、8/11 の四角、8/12
  のドット＋四角は前回と同じ見え方で、悪化は無い
- ToDo 型の行が日付ファイル側に混ざる件（reviewer 指摘の修正）は、
  用意したテストデータでは日付ファイル側に ToDo 型の行を混ぜていないため、
  画面では再現・確認していない。`mise run test` の新規テストが通っている
  ことのみで確認した
