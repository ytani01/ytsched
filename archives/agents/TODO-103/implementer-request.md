# TODO-103 implementer への依頼

週間表示に「月間ミニカレンダー」を足す。項目の本文は `TODO.md` の
TODO-103 にある。

- 週間表示（検索モードではない表示）の日曜日の下に、2 ヶ月分の月間
  ミニカレンダーを横に並べて出す
- 出す月は「その週の月曜が含まれる月」と「その翌月」
- 各日の下に、予定があることをドットで示す
- 日付をタップしたら、その日へジャンプする
- 細かいデザインは任されている

## 決めてあること（この通りに実装する）

### 置き場所

`main.html` の `.my-week-panel` の中、日付ブロック（`for sched_ent`）の
ループの後ろ。週パネルごとに 2 ヶ月分を持つ。**検索モードでは出さない**
（週の区切りに合わず、`weeks` も 1 要素のため）。

### サーバ側

1. `sched_load.py` に dataclass を 2 つ足す。
   - `MonthCalDay`: `date` / `in_month`（その月の日か。前後の月の
     埋めセルは `False`）/ `has_sched`（予定があるか）
   - `MonthCal`: `year` / `month` / `weeks`（`list[list[MonthCalDay]]`。
     月曜始まりの 7 個ずつ）
2. `SchedLoader` に `load_month_cal(year, month) -> MonthCal` を足す。
   - 予定の有無は `SchedData.sdf_exists(date)` で見る。**ファイルを
     開かない**ので軽い。ToDo は数えない。フィルタ・検索は反映しない
   - 同じ月が複数の週パネルで要るので、`SchedLoader` のインスタンスに
     dict のキャッシュを持たせて 1 リクエスト内で使い回す
     （`SchedLoader` はリクエストごとに作られる）
3. `SchedWeek` に `month_cals: list[MonthCal]` を足し、
   `MainHandler.mk_weeks()` で詰める。検索モードは空リスト。

### テンプレート・CSS・JS

- 日付セルのタップは `scrollToDate('{{ url_prefix }}', 'YYYY-mm-dd')`
  （`nav.js`）。DOM にある週なら週を移してスクロールし、無ければ
  `doGet()` に倒れる。**既存の日付セルと同じく `onmousedown` で登録
  する**（ドラッグとの区別は `swipe.js` に任せる）
- 前後の月の埋めセル（`in_month` が偽）はタップさせない
- 今日と、その週パネルが表示している週の 7 日は見分けが付くようにする
- CSS は `my.css` に `.my-mini-cal-…` で足す。既存の命名・色の使い方に
  合わせること
- 新しい JS ファイルは作らない

## 確かめること

- `mise run fmt` / `lint` / `typecheck` / `uv run pytest` が緑
- テストを足す。`load_month_cal()` の単体テスト（月初・月末の曜日、
  予定あり・なしの日、ディレクトリが無い月）と、週間表示の HTML に
  ミニカレンダーが 2 ヶ月分出て、検索モードでは出ないこと
- アプリの起動確認は `--datadir` に一時ディレクトリを指定する

## 文書

- `src/README.md` に、ミニカレンダーの持ち方（`SchedWeek.month_cals` と
  `load_month_cal()`、予定の有無を `sdf_exists()` で見ること）を短く足す

## 報告

`archives/agents/TODO-103/implementer-report.md` に書く。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内で。
