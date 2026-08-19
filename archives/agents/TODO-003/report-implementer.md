# TODO-003 implementer の報告

## 変更・作成したファイル

- `pyproject.toml`（変更）
  - `[dependency-groups] dev` に `pytest>=9.0.2` と `pytest-cov>=7.0.0`
  - `[tool.pytest.ini_options]` は `tmr` と同じくコメントのまま置いた
- `tests/helpers.py`（新規）
  - `make_app()`: `webapp.WebServer` と同じ設定の `Application` を、
    `datadir` だけ差し替えて作る（`autoreload` は付けない）
  - `make_handler()`: リクエストを送らずに handler を作る
    （`load_conf()` などを直に試すため。`connection` は Mock）
- `tests/test_ytsched.py`（新規、99 件）
  - `htmlstr2text()` / `text2htmlstr()` の変換表と往復
  - `SchedDataEnt`: `mk_dataline()`、`search_str()`、`get_timestr()` 4 通り、
    `get_sortkey()` の 3 分岐と並び順、`is_*()` の境界、`new_id()` の一意性
  - `SchedDataFile`: `date2path()`（日付あり / ToDo）、`load()`
    （utf-8・euc_jp、ファイル無し、休日、整列、時分の `% 24` / `% 60`）、
    `save()`（`.bak` 退避、ディレクトリ作成、空のとき）、
    `add_sde()` / `del_sde()` / `get_sde()`、**保存 → 読み直しの往復**
  - `SchedData`: キャッシュのヒット・ミス、LRU の並び、破棄、
    `get_sde()` / `add_sde()` / `del_sde()`
- `tests/test_handler.py`（新規、11 件）
  - `Conf.cgi` の読み書きの往復（タブ区切りのまま）、上書き、空の値、
    ファイル無し、未知のキー
  - `days2y_offset()`（0・正負・単調性）
  - import 時に標準出力へ何も出ないこと（別プロセスで確認）
- `tests/test_web.py`（新規、36 件、`tornado.testing.AsyncHTTPTestCase`）
  - `MainHandler`: `GET /`・`/ytsched`・`/ytsched/` が 200、テンプレートが
    展開されている、`date` / `year,month,day` / `cur_day` / `filter_str`
    （`!` 付きも）/ `search_str` / `search_n` / `todo_days` の各引数、
    設定が `Conf.cgi` に保存されて次回も効くこと、不正な正規表現でも 200、
    ToDo の表示（期限日・今日の欄・`todo_days` の範囲外）
  - `cmd=add` → `cmd=update` → `cmd=del` がデータファイルに反映されること、
    ToDo は `ToDo.cgi` へ入ること、ToDo 完了時に今日の予定へ移ること
  - `EditHandler`: 新規・既存・ToDo の既存
- `tests/test_webapp.py`（新規、5 件）
  - `datadir` が作られること、`~` が展開されること、
    `Application` の設定、webroot がパッケージに同梱されていること

`src/ytsched/` は一切変更していない。

## 自分で確かめたこと

- `uv sync` → pytest 9.1.1 / pytest-cov 7.1.0 が入る
- `uv run pytest` → **140 passed, 6 xfailed**（約 2.5 秒）
- `uv run pytest --cov=ytsched --cov-report=term-missing` → 全体 87%
  - `handler.py` 100%、`ytsched.py` 97%、`main_handler.py` 92%、
    `edit_handler.py` 95%、`webapp.py` 82%
  - `__main__.py` は 0%（後述）
- `uv run pytest --runxfail` で、6 件の xfail が**狙った理由で落ちている**
  ことを確認した（`TypeError`、`ValueError`、`DAYS_YEAR=...` の出力、
  `autoreload=True`、既定値が `datetime.date`、`warning` の呼び出し）
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、
  `GET /ytsched/` が 200 を返すことを確認した（ポート 10185、確認後に停止）
- `~/ytsched` はこの環境に存在しないままで、実データには触れていない
  （テストは `tmp_path` のみ）

## 既知のバグの扱い（xfail を付けたもの、6 件）

いずれも `@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)`。

| テスト | 対象 |
| --- | --- |
| `test_ytsched.py::test_set_time` | `'02d' % t1[0]` |
| `test_ytsched.py::test_sde_init_date_default_is_not_fixed` | `date=datetime.date.today()` |
| `test_ytsched.py::test_get_sdf_cache_miss_is_not_warning` | 正常系の `warning` |
| `test_handler.py::test_load_conf_line_without_tab` | `load_conf()` の `ValueError` |
| `test_handler.py::test_import_prints_nothing` | `print('DAYS_YEAR=...')` |
| `test_webapp.py::test_autoreload_is_not_forced` | `autoreload=True` |

TODO-005 の一覧のうち、**テストを書かなかったもの**（外から見える挙動が
無いため。TODO-005 で直しても、テストの追加・修正は要らない）:

- `main_handler.py` の `if sde.date == datetime.date(2021, 3, 1):`
  （デバッグログを出すだけの残骸）
- `HandlerBase.__init__` が `super().__init__()` を最後に呼んでいる
- `webapp.py` の `except Exception as ex: raise ex`
  （送出される例外は同じで、トレースバックの見え方が変わるだけ）

## 単独で決めた判断

1. **`[tool.pytest.ini_options]` はコメントのままにした。**
   `tmr` に揃えた。有効にすると毎回カバレッジ計測が走って遅くなり、
   `-k` で 1 件だけ流したいときに邪魔になる。カバレッジは
   `--cov=ytsched --cov-report=term-missing` を明示して見る。
2. **`pytest>=9.0.2` / `pytest-cov>=7.0.0`** — 版数の下限は `tmr` の写し。
3. **共通部品を `tests/helpers.py` に置いた。** `AsyncHTTPTestCase` は
   `unittest.TestCase` なので fixture を引数で受け取れず、`conftest.py` の
   fixture では `get_app()` から使えない。`tests/` に `__init__.py` は
   置いていない（`tmr` と同じ）ので、`from helpers import ...` で読める。
4. **`AsyncHTTPTestCase` では `tmp_path` を autouse の fixture で受け取り、
   `self.datadir` に入れた。** 引数では受け取れないため。実データには
   触れないという条件は満たしている。
5. **テスト用の `Application` は `autoreload` を付けていない**（依頼の
   許可どおり）。`webapp.py` 側は触っていない。
6. **`test_set_time` は `sde.time == '09:05-10:30'` を期待にした。**
   TODO-005 の「`%` 抜け」をそのまま直した場合の結果。もし TODO-005 で
   `time_start` / `time_end` を設定する形に作り替えるなら、
   **このテストは書き直しが要る**（`set_time()` が設定する `self.time` は
   他のどこからも使われていない）。
7. **既定値 `date=datetime.date.today()` は、シグネチャの既定値が
   `datetime.date` でないことを assert した。** 「`SchedDataEnt().date` が
   今日になる」は、モジュールを読み込んだ日が今日である限り**今でも
   通ってしまう**ので、strict xfail にできない。`None` 番兵でも他の形でも
   通る書き方にしてある。
8. **import 時の `print` は別プロセス（`subprocess`）で確認した。**
   同一プロセスでは import 済みで再現しないため。
9. **TODO-006 に関わる箇所は `not sde.time_start` の形で書いた。**
   `''` でも `None` でも通る。
10. **`save()` で中身が空のときにファイルが消える挙動は、現状のまま
    テストに固定した**（`test_save_empty_removes_file`）。最後の 1 件を
    消したらファイルごと無くなる、という意図的な作りに見えるため。
    仕様として違うなら、TODO-005 とは別に項目が要る。

## 気づいたが直さずに残したもの

TODO-005 の一覧に**無い**もの。テストも書いていない（依頼どおり）。

1. **`handler.load_conf()` の `line.split('\t', maxsplit=2)`**
   — `maxsplit=2` だと最大 3 個に分かれるので、**値にタブが含まれると
   `ValueError`** になる。`maxsplit=1` が正しい。タブの無い行の件
   （TODO-005）とは別の不具合。
2. **`SchedDataFile.save()` / `handler.save_conf()` / `load_conf()` が
   `encoding=` を指定していない** — ロケール依存になる。今の環境は
   UTF-8 なので通るが、`LANG=C` では日本語の保存で落ちる。
   `load()` 側は utf-8 → euc_jp を明示しているので、書く側だけ非対称。
3. **`SchedData.get_sdf()` の破棄数** — `int(cache_size * 0.1)` なので
   `cache_size < 10` だと 0 件になり、**キャッシュが上限を超えて増え
   続ける**。既定の 20000 では問題にならない。
4. **`SchedDataFile.load()` は 1 行 7 項目を前提にしている** — 項目が
   足りない行があると `IndexError`。壊れたデータファイルへの備えが無い。
5. **保存 → 読み直しで `detail` の末尾に `\n` が 1 つ増える** — `load()`
   が行末の改行を含めたまま `htmlstr2text()` に渡すため。`mk_dataline()`
   が `rstrip('\n')` するので実害は無く、往復は安定している。
6. **`MainHandler.get()` の先頭の `modified_sde_id = self.get_argument(
   'sde_id', '')` は、直後に `None` で上書きされる** — 死んだコード。
7. **同じく `MainHandler.get()` の `search_str` の処理が 2 回ある**
   （109〜123 行と 252〜267 行）。前半の結果は後半で上書きされるが、
   前半でも `set_conf()` が走るので、`Conf.cgi` への書き込みが二度
   起きうる。

## うまくいかなかったところ・残した穴

- **`src/ytsched/__main__.py` のカバレッジが 0%。** CLI（`click`）は
  依頼の対象範囲に無いので手を付けていない。`x_data1` サブコマンドと
  `webapp` サブコマンドは、テストから一度も呼ばれていない。
- `main_handler.py` の残り 8%（92% 到達）は、ほとんどが
  `re.error` を握り潰す分岐と、条件が同じときの `pass` の枝。
  不正な正規表現の扱いは TODO-012 で決めることなので、
  「500 にならない（200 が返る）」だけを固定して深追いしていない。
- `my_logger.py` の `dbg` に int を渡す経路は未テスト（TODO-007 で
  廃止予定のため）。

---

## reviewer 指摘への対応

`src/ytsched/` は引き続き変更していない。直したのはテストだけ。

### A. 指摘 1 — `set_time()`（利用者の決定 1 に合わせた）

`test_set_time_none` と `test_set_time` を 1 つにまとめ、
**`test_set_time_is_dead_code`** にした（`tests/test_ytsched.py`）。
xfail は付けていない。

- `hasattr(SchedDataEnt, 'set_time')` を assert
- 時刻を渡すと `TypeError` になることを `pytest.raises` で固定
- 時刻を渡さないときだけ通り、`self.time` が `':-:'` になることを固定
- docstring に「死にコードなので TODO-005 で丸ごと削除する。
  消したらこのテストも消すこと」と書いた

TODO-005 で `set_time()` を消すと `hasattr` の assert が落ちるので、
「このテストも消せ」と分かる。

### B. 指摘 2 — 空振りしていた assert

`test_filter_str` と `test_search_str`（`tests/test_web.py`）を、
**絞り込む語（`病院` = 場所）と表示を確かめる語（`歯医者` = 件名）を
分ける**形に直した。`test_filter_str_negative` /
`test_saved_filter_str_is_reused` と同じやり方。docstring にも理由を書いた。

**直したあとに、壊れ方を 2 通り作って確かめた**（一時的な pytest プラグインで
`SchedDataEnt.search_str()` を差し替え、`src/` は触っていない）:

1. 絞り込みが**全件を消す**壊れ方（`search_str()` が常に `''`）
   → `test_filter_str` / `test_search_str` を含む 6 件が落ちた
   （直す前の書き方では、この 2 件は通ってしまっていた）
2. 絞り込みが**何も除外しない**壊れ方（`search_str()` が全語を含む）
   → `test_filter_str` / `test_search_str` を含む 5 件が落ちた

両方向の壊れ方を捉えられている。

**他のテストも一通り見直した**（引数の値がそのまま本文に出るものが無いか）。

- `test_todo_with_filter_str` / `test_todo_with_search_str` /
  `test_search_n_limits_days` — reviewer の言うとおり空振りしていない。
  上の壊れ方 1 または 2 で落ちることを確認した
- `test_date_argument` / `test_year_month_day_arguments` /
  `test_cur_day_argument` — 確かめている `id="date-2021-03-01"` は
  日付ごとの描画で生成されるもので、引数の echo ではない
- `test_sde_is_displayed` / `test_add_is_displayed` / `test_del` /
  `EditHandler` の各テスト — 確かめる語はデータファイル由来で、
  同じリクエストの引数には渡していない
- `test_todo_days` / `test_search_n` / `test_filter_str_is_saved` —
  本文ではなく `Conf.cgi` の中身を見ているので空振りしない
- `test_get_new` の `value="2021-03-01"` だけは `date` 引数の echo だが、
  「新規の編集画面に日付が入る」ことの確認そのものなので、そのままにした

### C. 指摘 3 — `detail` の `rstrip('\n')`

`test_load` と `test_save_and_load_round_trip` の 2 か所を**直値**にした。

- `assert sde.detail == 'a\nb\n'`
- `assert sde2.detail == sde.detail + '\n'`

どちらにも「保存 → 読み直しで末尾に `\n` が 1 つ増えるのが現状」と
コメントを付けた。

### D. 指摘 9 — `test_load_conf_line_without_tab`

2 つに分けた（どちらも strict xfail のまま）。

- `test_load_conf_empty_line` — `'ToDo_Days\t365\n\n'`。docstring に
  「`if line:` は `'\n'` を真と判定するので、空行でも `split('\t')` されて
  `ValueError` になる」と書いた
- `test_load_conf_line_without_tab` — `'ToDo_Days\t365\nbroken\n'`

TODO-005 では**両方**の対処が要る（片方だけ直すと、もう片方が
strict xfail のまま落ち続ける）。

### E. 指摘 10 — `test_save_empty_removes_file`

docstring に但し書きを足した。「`.bak` は残るので中身は失われず、
意図的な作りに見えるため現状のまま固定した。仕様として違うなら、
TODO-005 とは別に項目が要る」。

### 直さなかったもの

指摘 4（`new_id()` の ID 衝突）、5（イベントループ）、
6（`helpers.make_app()` の二重管理）、7（`&nbsp:` の書き損じ）、
8（時分の丸め）は、指示どおりそのままにした。

### 直したあとの確認

- `uv run pytest` → **140 passed, 6 xfailed**（テスト項目は 146 件で変わらず）
- `uv run pytest --runxfail` → **6 failed, 140 passed**。6 件とも
  狙った理由で落ちている（`ValueError` ×2、`DAYS_YEAR=...` の出力、
  `autoreload=True`、既定値が `datetime.date`、`warning` の呼び出し）
- `uv run pytest --cov=ytsched --cov-report=term-missing` → 全体 87%（変化なし）
- 行長 78 を超える行が無いことを確認

**xfail は 5 件ではなく 6 件のまま**になった。A で 1 件減らした
（`test_set_time` の xfail を廃止）が、D で 1 件増えた（空行の分を
分けたので、`Conf.cgi` 関係の strict xfail が 1 件 → 2 件）。
差し引きで 6 件。A・D の両方の指示を満たすと、この数になる。
