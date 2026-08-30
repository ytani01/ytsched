# TODO-129. 月間ミニカレンダーの色分けと ToDo の印

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort medium | implementer + verifier + reviewer |
| 消費 | output 34,273 / cache_creation 316,103 / 概算 $4.9 |
|      | main 57% + verifier 17% + implementer 15% + reviewer 12%（料金の割合） |

分担と各担当の報告は
[archives/agents/TODO-129](../agents/TODO-129/README.md) にある。

## きっかけ

月間ミニカレンダー（TODO-103）は、予定があるかどうかを青いドット 1 つで
表すだけだった。重要な予定や休日、ToDo の締切が月のどこにあるかが
分からない。

## やったこと

### 背景色

優先度は **祝日・日曜 ＞ 土曜 ＞ 表示中の週 ＞ それ以外**。

| 条件 | 色 |
|---|---|
| 祝日（`type` が「休日」「祝日」）・日曜 | `#FFCCCC`（週表示の `.my-wday-6` と同じ） |
| 土曜 | `#FFEEEE`（週表示の `.my-wday-5` と同じ） |
| 表示中の週 | `#FFF` |
| それ以外の週 | `#E4E4E4` |

表示中の週は `#FFF6C0`（黄色）から白に変えた。前後の月の埋めセル
（`.my-mini-cal-day-out`）には曜日の色を付けない（テンプレート側で
`in_month` のときだけクラスを足す）ので、薄いグレーのままになる。

**CSS は記述順で優先度が決まる。** どれも単一クラスで詳細度が同じなので、
優先度の低いものから順に書いてある。

### 印

| 条件 | 印 |
|---|---|
| 通常の予定がある | 丸（`.my-mini-cal-dot`、`#28F`） |
| うち重要が 1 件でもある | 丸を赤に（`.my-mini-cal-dot-important`、`#E33`） |
| ToDo の締切がある | 四角（`.my-mini-cal-sq`、`#28F`） |
| 両方ある | 丸と四角を並べる（`.my-mini-cal-marks`） |

四角は丸と同じ色にして、**形だけで区別する**。

### 実装

- `src/ytsched/sched_load.py`
  - `MonthCalDay` に `has_important` / `is_holiday` / `has_todo` を足した
  - `load_month_cal()` を、`SchedData.sdf_has_sde()`（ファイルの大きさ
    だけを見る）から `get_sdf(date).sde`（**中身を読む**）に変えた。
    判定は既存の `SchedDataEnt.is_important()` / `is_holiday()`
  - ToDo の締切は日付ごとのファイルに無い（`date=None` の 1 ファイルに
    入っていて `sde.date` が締切）ので、`_get_todo_dates()` で締切日の
    集合を 1 リクエストにつき 1 回だけ作り、引くだけにした。フィルタ・
    検索・`todo_days` は反映しない（ミニカレンダーは元からそう）
- `src/ytsched/webroot/templates/main.html`・
  `src/ytsched/webroot/static/css/my.css`・`tests/test_main_handler.py`

### 決めたこと

- **ミニカレンダーの各日のファイルを開く。** `SchedData` のキャッシュに
  載るので 2 回目以降は速い。reviewer が `LoadMonths` の既定 1 と上限 24
  で 1 リクエストに要る日数を数えたところ、一覧側が元から読む範囲と
  ほとんど重なり、純増は数十日だった（キャッシュの上限 2000 に対して
  十分小さい）
- **取り消し済み（「(欠)」「(キャンセル)」）は赤ドットにしない。**
  先頭が `(欠` なので `is_important()` が False になり、実装上そうなる

### reviewer が見つけたこと

**日付ファイルに ToDo 型の行が混ざっていると、印が完全に消える。**
変更前は行数だけを見ていたので何かは出ていたが、変更後は通常の予定から
除かれ、`_get_todo_dates()`（`ToDo.jsonl` しか見ない）にも入らない。
正常な操作では `SchedUpdater` が ToDo を `ToDo.jsonl` へ書くので混ざら
ないが、`migrate` したデータや手で直したファイルでは起こりうる。

実データ（日付ファイル 6737 個）を調べたところ **0 件**だったが、
日付ファイル側の ToDo 型も四角のほうで拾うようにして、印が消えない
ようにした（テストを 1 件追加）。

### verifier が見つけたこと

**表示中の週の白と、それ以外のグレーの差が小さい。** 最初は `#F0F0F0`
だったが、キャプチャを見た利用者の判断で `#E4E4E4` に濃くした。

## テスト

- `mise run test` — 553 件すべて通過
- `mise run lint` — ruff・basedpyright・mypy・ESLint すべて通過
- verifier が一時ディレクトリにテストデータ（ふつうの予定・重要・
  取り消し済み・平日の祝日・ToDo 締切のみ・ToDo と予定の両方・予定なし）を
  作って 412px と 800px を撮り、背景色の優先度・赤ドット・四角の並びを
  画像で確認した
