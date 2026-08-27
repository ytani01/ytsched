# TODO-088 implementer への依頼

`load_sched()` を「1 週ぶんを組み立てる」と「検索結果を集める」に分け、
一覧の組み立てを `MainHandler` から出す。**挙動は一切変えない**
（返す HTML がバイト単位で今までと同じになること）。

TODO-087 で `sched_update.py` が増えているので、そちらの形（モジュールの
書き出し、docstring の付け方）に揃えること。

## 決めたこと（main が決めた。設計はこのとおりに作ること）

### 1. 新しいモジュール `src/ytsched/sched_load.py`

**tornado を import しない。** `SchedData` / `SchedDataEnt` と
`handler_util` だけを使う。

```python
@dataclasses.dataclass
class SchedLoadCond:
    """一覧を組み立てるときの条件 (TODO-079・TODO-088)。"""

    filter_re: re.Pattern[str] | None
    filter_neg: bool
    todo_days_value: int
    todo_today_sde: list[SchedDataEnt]
    todo_by_date: dict[datetime.date, list[SchedDataEnt]]


@dataclasses.dataclass
class SchedSearchCond:
    """検索だけが使う条件 (TODO-088)。"""

    search_re: re.Pattern[str]
    search_n: int


class SchedLoader:
    """スケジュールを読み集める (TODO-088)。"""

    __log = getLogger(__qualname__)

    #: 1 件も当たらないときに諦める日数 (元 MainHandler.SEARCH_MODE_DAYS)
    SEARCH_MODE_DAYS = 365

    def __init__(self, sd: SchedData) -> None: ...

    def load_todo(self, filter_re, filter_neg, search_re, todo_days_value): ...
    def mk_todo_by_date(self, search_re, todo_days_value, todo_sde): ...
    def load_week(self, date, cond) -> tuple[list[dict], date, date]: ...
    def search(self, date, cond, search_cond) -> tuple[list[dict], date, date]: ...
```

module 直下の関数として `filter_match(filter_re, filter_neg, sde)` と
`search_match(search_re, sde)` も、いまの `MainHandler` から**そのまま**
移す（`self` を使っていないため）。

- **`SchedLoadCond` から `search_re` / `search_n` を外す**
  （検索側 = `SchedSearchCond` の持ち物にする）
- **`SchedLoadCond` から `todo_sde` も外す。** どこからも読まれていない
  （`mk_todo_by_date()` の引数として渡すだけで、`load_sched()` は
  見ていない）
- **`search_mode` プロパティは消す。** 検索かどうかは、呼ぶ側が
  `search()` と `load_week()` のどちらを呼ぶかで表す

### 2. `load_sched()` を 2 つに分ける

いまの `load_sched()` の `while` の中には `search_mode` の分岐が 4 か所
ある。**分岐を残したまま 2 つに写すのではなく、それぞれのモードに要る
道だけを書く。**

共通部分（1 日ぶんを集める）は private メソッドにまとめる。名前は
`_load_day()` でよい。返すのは、いまの `sched` の 1 要素
（`{"date": ..., "is_holiday": ..., "sde": [...]}`）と、
**その日にファイルから当たった件数**（検索の打ち切りに使う。ToDo は
数えない。いまの `search_count += 1` が `sdf` の中の `sde` だけを
数えているのと同じ）。

`load_week(date, cond)`:

- `monday = date - timedelta(date.weekday())`、
  `date_from = monday`、`date_to = monday + timedelta(6)`
- 月曜から日曜まで 7 日ぶん、**1 件も当たらない日も落とさずに**並べる
- ToDo は `cond.todo_days_value >= 0` のときだけ混ぜる。
  `cond.todo_today_sde` は**今日の欄にだけ**足す
- 返り値は `(sched, date_from, date_to)`。`sched` は日付の昇順
  （いまの `sched[::-1]` と同じ並び）

`search(date, cond, search_cond)`:

- `date_to = date`、`date_from` の初期値は
  `date - timedelta(handler_util.SEARCH_MODE_MAX_DAYS)`
- 打ち切りの条件は**いまのまま**。`date` の翌日から 1 日ずつ古い方へ
  進み、ループの先頭で、**1 件以上当たっている**ときに限り
  - 当たった件数が `search_cond.search_n` 以上 → `date_from = date1` で終了
  - `date1 <= date - timedelta(SEARCH_MODE_DAYS)` → `date_from = date1` で終了
- ファイルが無い日は開かない（`sdf_exists()`。TODO-028）
- **1 件も当たらなかった日は並べない**（ToDo だけの日は並べる。
  いまの `if search_mode and not out_sde: continue` と同じで、
  ToDo を足したあとに見ている）
- `cond.todo_today_sde` は**混ぜない**
- 返り値は `(sched, date_from, date_to)`、`sched` は日付の昇順

**ここは挙動が変わりやすい。写す前に、いまの `load_sched()`
（`main_handler.py`）を最後まで読んで、条件の順序を確かめること。**

### 3. `MainHandler.get()` 側

- `initialize()` で `self._loader = SchedLoader(sd)` を作る
  （TODO-087 の `self._updater` と同じ形）
- `search_mode` は `search_re is not None` で今までどおり 1 回だけ決め、
  テンプレートへも今までどおり渡す
- 週の並び（`weeks`）を組み立てるところは、`get()` から
  `mk_weeks()` のような private メソッドへ出す。`get()` の中に
  `for offset in range(...)` を残さない
- **検索モードの `weeks` の `monday` を `None` にしない**（TODO-091 で
  dataclass にするときに、`None` になる型を残さないため）。
  検索でも `date` を含む週の月曜を入れておき、**テンプレート側で
  `data-monday` を出すかどうかを `search_mode` で分ける**:

  ```
  {% if w['monday'] %}data-monday="{{ w['monday'] }}"{% end %}
   ↓
  {% if not search_mode %}data-monday="{{ w['monday'] }}"{% end %}
  ```

  出力される HTML は今までと同じ（通常モードでは必ず出て、検索モード
  では出ない）。**テンプレートの変更はこの 1 行だけ**
- `compile_re()` / `compile_filter()` / `compile_search()` は
  `MainHandler` に残す（引数の変換の側）
- `MainHandler.SEARCH_MODE_DAYS` は `SchedLoader` へ移すので消す。
  `DELTA_DAY1` はテンプレートへ渡しているので `MainHandler` に残す

## 変えないこと

- 画面に出るもの、`conf.json` に書かれるもの、HTTP のステータス
- `mk_todo_by_date()` が `search_match()` をもう一度かけているところ
  （無駄なのは分かっているが、直すのは TODO-094）
- `SEARCH_MODE_DAYS` / `SEARCH_MODE_MAX_DAYS` という名前
  （直すのは TODO-094）
- `load_sched()` が返す `list[dict]` を dataclass にすること
  （TODO-091）
- テンプレートの掃除（TODO-092）、`sd=self._sd` を渡すのをやめること
  （TODO-091）

## テスト

`tests/test_main_handler.py` の `TestLoadSchedScan` が
`handler.load_todo()` → `handler.mk_todo_by_date()` → `handler.load_sched()`
を直に呼んでいる（`call_load_sched()`）。

- 呼び先を `SchedLoader` に合わせて直す。検索モードのケースは
  `search()`、通常モードのケースは `load_week()` を呼ぶ
- `test_mk_todo_by_date_is_called_once_per_request` は
  `SchedLoader.mk_todo_by_date` にパッチを当てる形へ
- **テストの期待値（何日ぶん出るか、どの日が出るか）は変えない。**
  変えなければ通らないところが出てきたら、直さずに報告に書くこと

## 済んだら

- `uv run ruff format` → `ruff check` → `basedpyright` → `mypy` →
  `pytest` を、直し終えてからまとめて走らせる
- `src/README.md` は **main が直す**ので触らない
- 報告は `archives/agents/TODO-088/implementer-report.md`
