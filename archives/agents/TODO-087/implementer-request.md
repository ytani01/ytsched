# TODO-087 implementer への依頼

`MainHandler` から**更新の実行**を出す。挙動は一切変えない。

## 決めたこと（main が決めた。設計はこのとおりに作ること）

### 1. `post()` は `main_handler.py` に残す

TODO.md のチェック項目は `post()` も外へ出すと書いてあるが、**残す**。
`post()` は

- 4 つの `get_conf_arg()`（`conf.json` への保存）
- `get_date()`（表示する日付の決定）
- `mkurl()`（リダイレクト先の組み立て）

を使う。どれも「引数の変換」と「表示」の側の処理で、`MainHandler` に
残るもの。`post()` を基底クラスへ移すと、これらを一緒に引きずることに
なり、モジュールの役割がぼやける。**tornado の入口は `MainHandler` に
置き、実行の中身を外へ出す**形にする。

出す（＝ `main_handler.py` から消える）のは次の 5 つ。

`exec_update()` / `cmd_add()` / `cmd_del()` / `fix_todo_done()` /
`get_modified_sde()`

残るのは `post()` / `exec_cmd()` / `get_update_form()`（新設） /
`get_date_arg()` / `get_time_arg()` / `get_deadline_str()`。

### 2. 新しいモジュール `src/ytsched/sched_update.py`

**tornado を import しない。** `SchedData` と `SchedDataEnt` だけを使う。

```python
@dataclasses.dataclass
class SchedUpdateForm:
    """更新フォームから受け取る値一式 (TODO-087)。"""

    cmd: str
    sde_id: str | None
    orig_date: datetime.date | None
    date: datetime.date | None
    time_start: datetime.time | None
    time_end: datetime.time | None
    sde_type: str
    title: str
    place: str
    detail: str
    deadline_date_str: str
    deadline_time_start_str: str
    deadline_time_end_str: str


class SchedUpdater:
    """``cmd`` (add/fix/update/del) を実行する (TODO-087)。"""

    __log = getLogger(__qualname__)

    def __init__(self, sd: SchedData) -> None: ...

    def exec_update(
        self, form: SchedUpdateForm
    ) -> tuple[datetime.date | None, str | None]: ...

    def get_modified_sde(
        self, date: datetime.date | None, sde_id: str | None
    ) -> SchedDataEnt | None: ...

    def fix_todo_done(...) -> tuple[...]: ...   # 今のまま
    def cmd_add(...) -> SchedDataEnt: ...       # 今のまま
    def cmd_del(self, date, sde_id) -> None: ...# 今のまま
```

- `exec_update()` は、いまの `exec_update()` から**引数の取り出し部分
  （`get_date_arg()` / `get_time_arg()` / `get_deadline_str()` /
  `get_argument()`）を除いた残り**。`cmd` は `form.cmd` を使う。
  `try` / `finally` の `self._sd.save()`、`cmd in ["add"]` のときに
  `sde_id = None` にするところ、ToDo 完了時の補正の条件
  （`form.deadline_date_str and not SchedDataEnt.type_is_todo(...)`）は
  **そのまま**。コメントも移す
- `get_modified_sde()` は、**404 を投げるのをやめて
  `SchedDataEnt | None` を返す**（tornado を知らないため）。
  見つからないときに 404 にするのは `MainHandler.exec_cmd()` の側。
  引数から `cmd` が要らなくなる（404 のメッセージに使っているだけ
  なので、呼び出し側で組み立てる）

### 3. `MainHandler` 側

- `initialize()` を上書きして `self._updater = SchedUpdater(sd)` を作る
  （`super().initialize(sd)` を先に呼ぶ）
- `get_update_form(cmd)` を新設。いまの `exec_update()` の前半にある
  引数の取り出しをそのまま移し、`SchedUpdateForm` に詰めて返す。
  **`orig_date` → `date` → 時刻 → その他、の順は変えない**
  （空でないのに読めない値を、書き込みが 1 つも起きる前に 400 で
  断るため。TODO-027）
- `exec_cmd()` は、`self._updater.exec_update(form)` を呼ぶ形に直す。
  **引数 `search_str` は使われていないので消す**（呼び出し側の
  `post()` では `search_str = ...` を `_ = ...` に変える。
  `conf.json` へ保存する副作用のために呼ぶのは今までどおり）
- `sde` が `None` のとき 404 を投げるのは `exec_cmd()` に置く。
  メッセージ・ステータス・引数は今と同じにすること

## 変えないこと

- 画面に出るもの、`conf.json` に書かれるもの、HTTP のステータス、
  ログの内容
- `SchedLoadCond` と表示側（`get()` / `load_sched()` など）は**触らない**
  （TODO-088 の範囲）
- 定数の置き場所（`CONF_KEY_*` など）

## テスト

- `tests/test_main_handler.py` の `spy_cmd_add()` が
  `MainHandler.cmd_add` にパッチを当てている。`SchedUpdater.cmd_add`
  へ変える（`from ytsched.sched_update import SchedUpdater`）
- `tests/test_web.py:1322` あたりの `mock.patch.object(MainHandler,
  "cmd_add", ...)` も同じ
- **テストの期待値は変えない。** 呼び先の名前だけを合わせる
- 新しく `tests/test_sched_update.py` を作らなくてよい（TODO-087 の
  範囲は移動。テストの拡充は別の項目）

## 済んだら

- `uv run ruff format` → `ruff check` → `basedpyright` → `mypy` →
  `pytest` を、直し終えてからまとめて走らせる
- `src/README.md` は **main が直す**ので触らない
- 報告は `archives/agents/TODO-087/implementer-report.md`
