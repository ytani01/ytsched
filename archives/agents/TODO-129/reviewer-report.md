# TODO-129 reviewer 報告

対象: `src/ytsched/sched_load.py` / `src/ytsched/webroot/templates/main.html` /
`src/ytsched/webroot/static/css/my.css` / `tests/test_main_handler.py`
（未コミット、`git diff` で見た差分）。コードは直していない。

## 指摘（確信度が高い順）

### 1. 日付ファイルに ToDo 型のエントリが混ざっているデータで、印が完全に消える

`src/ytsched/sched_load.py` の `load_month_cal()`（288〜352 行あたり）で、
`has_sched` / `has_important` / `is_holiday` はすべて
`sde_list = [sde for sde in self._sd.get_sdf(date1).sde if not sde.is_todo()]`
から作る。`has_todo` は別途 `_get_todo_dates()`（`ToDo.jsonl` だけを見る）
から引く。

正常な操作では `sched_update.py:285-290`（`cmd_add`/`cmd_edit` に相当する
コード）が `is_todo()` なエントリを必ず `self._sd.add_sde(None, ...)`
（＝ `ToDo.jsonl`）へ書くので、日付ファイル（`self._sd.get_sdf(date1)`、
`date1` は具体的な日付）に ToDo 型のエントリが混ざることは無い。

ただし `docs/data-format.md` に「専用のフィールドを持たず `type` の
先頭で判定する」とあるとおり、この区別は保存場所ではなく `type` 文字列
だけに拠っている。`ytsched migrate`（`src/ytsched/migrate.py`）は旧形式の
ファイルを 1 対 1 で変換するだけで、`is_todo()` による再配置はしていない
ように見える（`migrate_file()` 付近に `is_todo` への言及なし）。旧い
Perl CGI 時代のデータや、利用者が `.jsonl` を手で直したときに、日付
ファイル側に `type` が `□` で始まる行が残っていた場合:

- **変更前**: `sdf_has_sde()` はエントリ数だけを見るので、そのエントリが
  1 件でもあれば、その日にドットが出ていた（`type` が ToDo 型でも、
  「予定がある」という誤った表示だが、何かは出ていた）
- **変更後**: そのエントリは `sde_list` の生成時に除外され、かつ
  `_get_todo_dates()` は `ToDo.jsonl` の中身しか見ないので `has_todo` も
  偽になる。**その日はドットも四角も出ず、完全に無印になる**

依頼の 3 番の「旧データに混ざりうるか」への回答としては、通常の運用では
起きないが、`migrate` 由来または手編集のデータでは起こりうる、という
エッジケース。実データがそうなっているかは未確認（確かめていない）。

### 2. テンプレート側（クラス付与・マークの組み立て）を検証する自動テストが無い

`tests/test_main_handler.py` に足された 5 件はすべて
`SchedLoader.load_month_cal()` が返す `MonthCalDay` の属性
（`has_important` / `is_holiday` / `has_todo` / `has_sched`）を直接見るだけで、
`main.html` 側の

- `d.is_holiday or d.date.weekday() == 6` → `my-mini-cal-day-holiday`、
  `elif d.date.weekday() == 5` → `my-mini-cal-day-sat` という分岐
- `.my-mini-cal-marks` の中身（丸→四角の順、`has_important` での
  `my-mini-cal-dot-important` 付与）

を、実際にレンダリングされた HTML で確かめるテストは無い。祝日と日曜が
重なる日、予定と ToDo が両方ある日の実際の出力は自動テストでは押さえて
いない。

ただし、`TestMonthCal` の既存のテスト（TODO-103 由来）も同様に
`load_month_cal()` 止まりで、テンプレートの HTML までは見ていない。
今回に限った後退ではなく、この節全体の元々のテスト方針（判定ロジックは
Python 側、テンプレートは見ない）を踏襲したもの。

## 確認したが、問題は見当たらなかったこと

依頼 1 番の「`_month_cal_cache` の効き方も含めて、キャッシュの上限を
超えて追い出しが多発しないか」について、`LoadMonths` の既定 1・上限 24
それぞれで、1 リクエスト中に必要になるユニークな日数を簡易シミュレーション
した。

- `LoadMonths=1`: ミニカレンダーが要求する月は 3 か月ぶん、日数は 98 日
  （一覧側が元々読む 63 日と、ほぼ重なる）
- `LoadMonths=24`（上限）: ミニカレンダーが要求する月は 49 か月ぶん、
  日数は 1498 日（一覧側が元々読む 1449 日とほぼ重なり、純増は約 50 日）

`SchedData.DEF_CACHE_SIZE = 2000`（`src/ytsched/ytsched.py:759`、
コメントに「1 リクエストで開くファイル数は最大 1450」とある）に対して、
純増分は数十日程度で収まり、キャッシュの上限（2000）を超えて追い出しが
多発するような規模ではなかった。ミニカレンダーの週の範囲と一覧の週の
範囲がほぼ同じ月・週を指すため、想定していたほど新規のファイルオープンは
増えない。

CSS の記述順（依頼 4 番）も確認した。`.my-mini-cal-day`（既定）→
`.my-mini-cal-day-cur-week` → `.my-mini-cal-day-sat` →
`.my-mini-cal-day-holiday` の順で、すべて単一クラスのセレクタ（詳細度
同じ）なので、後に書かれたものが勝つ。祝日・日曜 ＞ 土曜 ＞ 表示中の週 ＞
既定、の優先度どおりに効く。`.my-mini-cal-day-out` は `color` しか
持たず `background-color` を上書きしないので、前後の月の埋めセルは常に
薄いグレーのまま（テンプレート側で `in_month` のときしか祝日・土曜の
クラスを足していないことと合わせて）意図どおり。

`_todo_dates`（依頼 2 番）は `SchedLoader` が `MainHandler.initialize()`
（`src/ytsched/main_handler.py:44`）でリクエストごとに新しく作られるので、
1 リクエストの生存期間しか持たない。ToDo が 1 件も無いときも
`get_sdf(None).sde` が空リストになるだけで例外にはならず、テストでも
確認されている。

## 判断が要る点

- 上記 1 の「日付ファイルに ToDo 型が混ざったデータ」は、現行データで
  実際に起きているかを確かめていない。起きているかどうかで、直すか
  どうかの判断が変わる
