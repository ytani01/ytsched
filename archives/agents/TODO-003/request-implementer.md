# TODO-003 implementer への依頼

`~/work/ytsched/TODO.md` の TODO-003 を読んでから始めること。

## やること

`tests/` を新規に作り、pytest でテストを整備する。**現状の挙動を固定する**のが
目的。TODO-005・TODO-006 の修正に進む前の土台になる。

### 1. dev 依存とテスト設定

`pyproject.toml` に `[dependency-groups] dev` を足し、`pytest` と
`pytest-cov` を入れる。`~/work/tmr/pyproject.toml` の書き方に揃える
（版数の下限の付け方も含む）。lint・型チェック（ruff / mypy /
basedpyright）は **TODO-004 の範囲なので入れない**。

`[tool.pytest.ini_options]` を書くかどうかは `tmr` に合わせて判断してよい
（`tmr` ではコメントアウトされている）。判断した理由を報告に書くこと。

### 2. `SchedDataEnt` / `SchedDataFile` / `SchedData` のユニットテスト

`src/ytsched/ytsched.py` が対象。最低限、次を押さえる。

- `htmlstr2text()` / `text2htmlstr()` — 変換表の各項目、改行と `<br />` の往復
- `SchedDataEnt`
  - `mk_dataline()` と `SchedDataFile.load()` の**往復**（保存して読み直すと
    同じ内容になる）。データ形式はタブ区切りで変えられないので、ここが
    いちばん大事
  - `get_timestr()` — 開始・終了の有無 4 通り（`':-:'` を含む）
  - `get_sortkey()` — 休日・`(` 始まり・それ以外で `':-:'` の置換が変わる分岐
  - `is_todo()` / `is_holiday()` / `is_important()` / `is_canceled()` /
    `type_is_todo()` — 真偽の境界（空文字列のとき）
  - `search_str()` の書式、`new_id()` が一意になること
- `SchedDataFile`
  - `date2path()` — 日付ありと `None`（ToDo）
  - `load()` — utf-8 と euc_jp の両方が読めること、ファイルが無いとき空リスト、
    休日が含まれると `is_holiday` が True、読み込み後に整列されていること
  - `save()` — 既存ファイルが `.bak` に退避されること、ディレクトリが
    無くても作られること、`self.sde` が空のときの挙動
  - `add_sde()` / `del_sde()` / `get_sde()`
- `SchedData`
  - `get_sdf()` のキャッシュヒット・ミス、LRU として並びが更新されること
  - `_cache_size` を超えたときの破棄（`CACHE_DISCARD_RATE`）
  - `get_sde()` / `add_sde()` / `del_sde()`

**ファイルを触るテストは必ず `tmp_path` を使う。**
`~/ytsched/data` の実データには絶対に触れないこと。

### 3. handler のテスト（`tornado.testing`）

`tornado.testing.AsyncHTTPTestCase` を使う。`webapp.py` の `WebServer` が
組み立てている `tornado.web.Application` と同じ設定を、テスト側で
`datadir` だけ `tmp_path` 相当に差し替えて作る。

- `HandlerBase` の `load_conf()` / `save_conf()` / `get_conf()` /
  `set_conf()` — `Conf.cgi` の読み書きの往復（**タブ区切りのまま**）
- `MainHandler` — `GET /ytsched/` が 200 を返し、テンプレートが展開されて
  いること（`{{` や `{%` が生で残っていない）
- `MainHandler` — `date` / `filter_str` / `search_str` / `todo_days` の
  各引数が効くこと
- `MainHandler` — `cmd=add` → `cmd=update` → `cmd=del` の一連が
  データファイルに反映されること
- `EditHandler` — `GET /ytsched/edit` が 200、新規と既存の両方
- `days2y_offset()` — `days == 0` と正負

`autoreload=True` はテストで問題になるかもしれない。なるなら、テスト側の
Application では外してよい（**`webapp.py` は直さない**。TODO-005 の範囲）。

## 既知のバグの扱い（重要）

TODO-005 に挙がっているバグを、**テストで「正しい挙動」として固定しない。**
バグに当たるテストは、**あるべき挙動を assert したうえで**
`@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)` を付けること。
`strict=True` にするのは、TODO-005 で直したときに xpass で失敗して
「マーカーを外せ」と気づけるようにするため。

TODO-005 に挙がっているもの（再掲）:

- `SchedDataEnt.set_time()` の `'02d' % t1[0]`（`%` 抜けで必ず TypeError）
- `SchedDataEnt.__init__` の既定値 `date=datetime.date.today()`
- `main_handler.py` の `print('DAYS_YEAR=...')`
- `main_handler.py` の `if sde.date == datetime.date(2021, 3, 1):`
- `handler.load_conf()` がタブの無い行で `ValueError`
- `HandlerBase.__init__` が `super().__init__()` を最後に呼んでいる
- `webapp.py` の `except Exception as ex: raise ex`
- 正常系のキャッシュミスを `warning` で出している
- `autoreload=True` が固定

TODO-006（型ヒント）で直る `time_start=''` のような箇所も、
**空文字列を正解として固定しない。** `None` でも `''` でも通るように書くか、
どうしても固定が要るなら理由を報告に書くこと。

**上の一覧に無いバグを見つけたら、直さずに報告に書く。** テストも
書かないでよい（TODO-005 に足すかどうかは main が判断する）。

## やらないこと

- **`src/ytsched/` のコードを直さない。** TODO-003 はテストを足すだけ。
  テストのためにどうしても直さないと進めない箇所があれば、**そこで手を止めて
  報告する**
- ruff / mypy / basedpyright / `mise.toml`（TODO-004 の範囲）
- `my_logger.py` の廃止（TODO-007 の範囲）

## 確認

自分でも `uv sync` と `uv run pytest` を通してから報告すること。
カバレッジも一度は見る（`uv run pytest --cov=ytsched --cov-report=term-missing`）。
最終的な確認は `verifier` が別に行うが、任せきりにしない。
