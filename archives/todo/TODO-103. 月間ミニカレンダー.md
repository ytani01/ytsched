# TODO-103. 月間ミニカレンダー

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 実施 | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 消費 | output 33,221 / cache_creation 507,707 / 概算 $8.4 |
|      | main 52% + implementer 24% + verifier 14% + reviewer 8% + wording 2%（料金の割合） |

分担は [archives/agents/TODO-103/](../agents/TODO-103/) にある。

## きっかけ

週間表示は 7 日分しか出ないので、前後の月のどのあたりを見ているかが
分からなかった。日曜日の下に 2 ヶ月分の月間ミニカレンダーを並べて、
月の中での位置と、予定がある日を一目で分かるようにする。

## やったこと

- `sched_load.py`: `MonthCalDay`（`date` / `in_month` / `has_sched`）と
  `MonthCal`（`year` / `month` / `weeks`）を足し、
  `SchedLoader.load_month_cal(year, month)` で 1 か月分を組み立てる。
  `weeks` は月曜始まりの 7 個ずつで、前後の月にはみ出す日付のセル
  （以下「埋めセル」）も含む。
  同じ月が複数の週パネルから要るので、`SchedLoader` のインスタンスに
  dict のキャッシュを持たせた（`SchedLoader` はリクエストごとに作られる
  ので、古い内容を返す道は無い）。
- `main_handler.py`: `SchedWeek.month_cals` に、その週の月曜が含まれる月と
  その翌月の 2 つを詰める（`mk_month_cals()`）。検索モードは空リスト。
- `main.html`: 週パネルの日付ブロックの後ろに、`<table class="my-mini-cal">`
  を 2 つ横に並べる。日付セルは `onmousedown="scrollToDate(...)"` で、
  DOM にある週ならページを読み直さずに移り、無ければ `doGet()` に倒れる
  （`nav.js` の既存の分岐にそのまま載せた）。前後の月の埋めセルには
  付けない。今日と、その週パネルが表示している 7 日は色を変えてある。
- `my.css`: `.my-mini-cal-*` を足した。既存の `.my-btn`（押したときの
  黄色）と `.my-date-block-today` の枠色 `#28F` を流用している。
- **予定の有無はファイルを開かずに見る。** 日ごとに 1 ファイルなので、
  1 か月分でも `stat()` が 31 回で済む。フィルタ・検索は反映せず、
  ToDo も数えない（軽さを優先した）。

reviewer から「その日の予定を全部削除しても、`save()` が空のファイルを
書くのでドットが消えない」という指摘があり、`SchedData.sdf_has_sde()` を
足して直した。キャッシュに載っていれば `sde` の数を、載っていなければ
ファイルの大きさを見る（どちらもファイルは開かない）。既存の
`sdf_exists()` は「開くかどうか」を決めるための最適化なので、そのまま
「予定あり」の印には使えなかった。

## テスト

- `mise run lint`・`mise run typecheck`: 緑。
- `uv run pytest`: 494 passed。1 件
  （`test_browser.py::test_tap_again_stops_auto_page_turn`）が落ちるが、
  この変更を `git stash` で外した状態でも同じ頻度で落ちる既存の
  タイミング依存のテストで、今回の変更が原因ではないことを確かめた。
- 足したテストは 14 本。`load_month_cal()` の単体テスト（月曜始まりで
  月初・月末を含む週まで並ぶ、`in_month`、`has_sched`、空のファイル、
  ディレクトリごと無い月、キャッシュ）、`sdf_has_sde()` の単体テスト、
  週間表示の HTML（2 ヶ月分出る、ドット、タップ、埋めセルはタップ
  できない、検索モードでは出ない）。
- 一時 datadir でアプリを起動し、画面で確かめた。月の組み合わせ、
  ドットの有無、読み込んだ範囲の内と外へのタップ、埋めセルが反応しない
  こと、今日と表示中の週の色分け、月をまたぐ週送り、検索したときに
  出ないこと、幅 412px で横スクロールが出ないこと。予定を削除したあとに
  ドットが消えることも、ファイルが 0 バイトで残っている状態で確かめた。
