# TODO-006. 型ヒントの整備

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

分担の理由と各担当の報告は
[archives/agents/TODO-006/](../agents/TODO-006/README.md) にある。

## きっかけ

`time_start: datetime.time = ''` のように、空文字列を `datetime.time`
として扱っている箇所が広い。既定値 `None` に `datetime.date` の注釈が
付いた implicit Optional も多く、TODO-004 で入れた mypy /
basedpyright が 35 件 / 28 件のエラーを出していた。

## やったこと

### 型そのものの修正

- `time_start` / `time_end` の既定値を `''` → `None` にし、注釈を
  `datetime.time | None` にした。**真偽判定（`if self.time_start:`）は
  1 か所も変えていない**（`''` も `None` も falsy なので同じ）
- implicit Optional（`date: datetime.date = None` など）を
  `datetime.date | None = None` に直した。ruff の `RUF013` が 10 件消えた
- `SchedData.get_sde()` / `SchedDataFile.get_sde()` の戻り値を
  `SchedDataEnt | None` にした（実際に `None` を返すため）
- `MainHandler.exec_update()` の `-> (datetime.date, str)` を
  `-> tuple[datetime.date | None, str | None]` にした。当初の指示は
  `tuple[datetime.date, str]` だったが、この関数は実際に `None` を返す
  （`cmd == "del"` では `modified_sde_id` が `None`、ToDo なら
  `date` が `None`）
- `_sdf_cache` のキーの型を `datetime.date | None` にした
  （ToDo を `date=None` のキーで扱っているため）。TODO-004 で入れた
  `datetime.date` は実体と合っていなかった

### 型を通すために書き換えた箇所

- `SchedDataEnt.__init__` の `sde_id` / `date` の代入を条件式 1 文に
  まとめた（属性が `str | None` と推論されるのを避けるため）。
  `new_id()` の呼び出し位置が `__init__` の末尾から先頭寄りに移るが、
  `new_id()` はインスタンス属性を読まないので結果は変わらない
- `SchedData.add_sde()` の `date` / `sde` から既定値 `= None` を外した。
  `sde=None` で呼ぶと `sorted(key=...)` で AttributeError になる、
  最初から意味の無い既定値だった。呼び出しは 5 か所とも 2 引数の位置引数
- `edit_handler.py` の `get_argument('todo_flag', False)` を
  `get_argument('todo_flag', '')` + `== 'true'` にした。tornado の
  `_get_argument` は marker でない `default` をそのまま返すので、
  `False == 'true'` も `'' == 'true'` も `False` で挙動は同じ
- `main_handler.py` の `todo_days_value` が `str | None` と `int` で
  使い回されていたのを、文字列用の `todo_days_str` に分けた

### reviewer の指摘への対応

- `get_sde()` が `None` を返しうるようになったため入れた
  `if sde is not None:` の guard で、**変更前は 500 になっていた経路が
  黙って 200 で通る**ようになっていた。`else` 側に `warning` を
  1 行足した（挙動は変えず、ログに残るようにしただけ）。
  根本原因（`date` が空の POST で ToDo ファイルへ書かれる）は
  この項目より前からあるもので範囲外なので、TODO-016 として立てた
- `SchedData` のクラス docstring がキャッシュのキーの型と
  食い違っていたので直した

## テスト

verifier が実際に実行して確かめた（`archives/agents/TODO-006/verifier-report.md`）。

| 確認 | 結果 |
| --- | --- |
| `uv run pytest tests` | 161 passed（変更前と同数） |
| `uv run mypy src tests` | 35 件 → **2 件**。残るのは `__class__` の 2 件で、TODO-007 で `my_logger.py` ごと消える範囲 |
| `uv run basedpyright src tests` | 28 errors, 2 warnings → **0** |
| `uv run ruff check --extend-select I src tests` | 97 件 → 87 件（差は `RUF013` の 10 件だけ。残りは TODO-015 / TODO-008 の範囲） |
| webapp の起動 | 一時 datadir で起動し `/ytsched/` `/ytsched/edit` とも 200。ログに例外なし |
| **データ形式** | 一時 datadir へ add / update / del を実際に POST し、`cat -A` で確認。7 項目のタブ区切り、時刻なしは `:-:`、時刻ありは `09:05-10:30`、終了時刻だけ空は `05:45-:` で**従来どおり** |
| 足した warning | 指摘どおりの経路（`date` を空にして非 ToDo を `cmd=add`）で `sde not found: ...` が出て、画面は 200 のままであることを確認 |

`time_start` / `time_end` を `None` にしたので、データ形式の確認が
いちばん重要だった。reviewer 側でも `time_start` / `time_end` の全参照
（`src` の `.py`、テンプレート、`tests`）を洗い、比較・連結・書式化に
生値を使っている箇所が 0 件であることを確認している。
