# TODO-021 implementer(2) の報告 — リファクタリング本体

## 結果

- **テストは 330 passed のまま**（着手時 330、A〜E の各段階でも 330）。
  **テストは 1 行も書き換えていない**（`git diff tests/` は
  implementer(1) が足した `test_settings_are_read` だけ）
- `ruff format --check` / `ruff check --extend-select I` /
  `basedpyright`（0 errors）/ `mypy`（Success）/ `pytest`（330 passed）
  すべて通っている
- **旧コードと新コードで、同じリクエストに対する応答が
  バイト単位で一致することを確かめた**（下の「自分で確かめたこと」2・3）

## 変更したファイル

| ファイル | 要点 |
| --- | --- |
| `src/ytsched/main_handler.py` | A・B・E。`get()` と `exec_update()` を分割し、メソッドを 9 つ追加 |
| `src/ytsched/ytsched.py` | C。`title_starts_with()` の追加、`is_todo()` の委譲、`get_timestr()`・`load()` の整理 |
| `src/ytsched/handler.py` | D。`get_conf()` を `dict.get()` へ、`__init__` の debug ログを 1 つに |
| `src/ytsched/__main__.py` | E。空の `DataFileApp.end()` と、その呼び出しを削除 |

`tests/` と `TODO.md` は触っていない。

## A. `MainHandler.get()` の分割

`get()` は約 250 行 → 136 行（うち 25 行は `render()` の引数）。
追加したメソッド:

| メソッド | 担当 |
| --- | --- |
| `get_conf_arg(arg_name, conf_key, default, *, empty_is_given)` | 設定値の取り出し 4 か所を 1 つに |
| `exec_cmd(search_str)` | `cmd` のブロック。3 つ目の戻り値が「描画したか」 |
| `get_modified_sde(cmd, date, sde_id)` | 更新後のデータの読み直しと 404 |
| `get_date(modified_date)` | `# set Date` のブロック |
| `get_sde_align()` | `# sde_align` のブロック |
| `compile_filter(filter_str)` | `(filter_re, filter_neg, filter_error)` |
| `compile_search(search_str)` | `(search_re, search_error)` |
| `load_todo(...)` | `# load ToDo` のブロック |
| `load_sched(...)` | `# load schedule data` のブロック。`(sched, date_from, date_to)` を返す |
| `search_match(search_re, sde)` | 散っていた 3 か所のマッチ |

### A-1. 設定値の取り出し（**揃っていない条件は残した**）

`get_conf_arg()` の分岐は次の 1 行で、**`empty_is_given` で差を残している**。

```python
if value is not None and (empty_is_given or value):
```

- `empty_is_given=True` → `value is not None`（`search_str` / `search_n`）
- `empty_is_given=False` → `value is not None and value` ＝ `bool(value)`
  （`todo_days` / `filter_str`）

`.lower()` と `int()` は呼び出し側に残した。`set_conf()` が `.lower()` の
前に来る順序、`search_n` の `set_conf()` が `int()` の前に来る順序も、
そのまま（空の `search_n` は今までどおり 500 になり、`SearchN` の保存だけ
先に済む）。**4 か所を呼ぶ順序も変えていない**（search_str → cmd → date →
todo_days → sde_align → filter_str → 正規表現 → search_n）。`Conf.cgi` の
キーの並びは保存順で決まるので、ここは動かせない。

`filter_str` の `get_argument("filter_str", "")` は、truthy 分岐なので
`None` と等価。`get_conf_arg()` 側の `None` 既定に寄せた。

### A-2. `search_match()`

`filter_match()` と同じ形にした。`search_re is None` なら `True`。
`get()` にあった 3 か所（ToDo の読み込み、日々のデータ、`todo_sde` の
差し込み）を `if not self.search_match(search_re, sde): continue` に置き換えた。

### A-3. ブロックの切り出しで気をつけた点

- `cmd == "update"` の `render()` → `exec_cmd()` の戻り値 3 つ目
  （`rendered`）で表し、`get()` 側が `return` する
- `date_from` は `load_sched()` から返す（ループの中で書き換わるため）
- `delta_day1` は**クラス定数 `DELTA_DAY1 = datetime.timedelta(1)` にした**
  （判断の理由は下記）

## B. `exec_update()` の分割

約 130 行 → 95 行。追加したメソッド:

| メソッド | 担当 |
| --- | --- |
| `get_date_arg(arg_name)` | 引数を日付として取り出す（`orig_date` / `date`） |
| `get_time_arg(arg_name)` | 引数を時刻として取り出す（`time_start` / `time_end`） |
| `get_deadline_str()` | `deadline_*` 3 つの取り出し（`-` の付加を含む） |
| `fix_todo_done(...)` | ToDo 完了時の補正。**4 つ受け取って 4 つ返す** |

条件は変えていない。

```python
if deadline_date_str and not SchedDataEnt.type_is_todo(sde_type):
    date, time_start, time_end, detail = self.fix_todo_done(
        deadline_date_str,
        deadline_time_start_str,
        deadline_time_end_str,
        detail,
    )
```

**`cmd_add()` の引数の並びは変えていない**（位置引数 8 つのまま）。
新しいデータ型も作っていない。

## C. `ytsched.py`

- `title_starts_with(prefix_list)` を足し、`is_important()` /
  `is_canceled()` をそこへ委譲。**先頭の `if self.title == ""` は落とした**。
  `TITLE_PREFIX_IMPORTANT`（5 個）と `TITLE_PREFIX_CANCELED`（7 個）に
  **空文字が無いことを目で確かめてから**落としている（空文字はどの接頭辞にも
  一致しないので `False` のまま）
- `is_todo()` → `type_is_todo(self.type)` へ委譲
- `get_timestr()` → `time2str()` を使う形にした。
  `if self.time_start:` は `time` が常に truthy（Python 3.5 以降、
  `time(0, 0)` も真）なので `is not None` と同じ。`time2str()` は `None` の
  ときだけ `None` を返し、それ以外は必ず `"HH:MM"`（truthy）なので、
  `or ":"` は元の分岐と一致する。`"%H:%M"` の直書きも消えた
- `load()` の `out2` を消して `return sorted(...)`

## D. `handler.py`

- `get_conf()` の `try` / `except KeyError` → `self._conf.get(name)`
- `__init__` の**属性への代入は 8 つとも明示のまま**残し、
  1 行ごとに付いていた debug ログを 1 つにまとめた
  （`setattr` やループにはしていない）

## E. 意味の無い記述

- `else: pass` 4 か所は、A-1 の `get_conf_arg()` にまとめた時点で消えた
  （`grep` で残っていないことを確認）
- `DataFileApp.end()`（空）と、`x_data1()` の `app.end()` を削除。
  **`try` / `finally` は残した**（`_log.info("end")` はそのまま）

## 挙動が変わっていないと言える根拠

### 1. テスト

- 着手時 330 passed → A・B・C・D・E の各段階で 330 passed → 最終 330 passed
- **テストは 1 行も書き換えていない。** 書き換えたくなる場面も無かった
- implementer(1) が「条件式をずらせば必ず落ちる」ことを 16 通りで
  確かめてある条件（`date1 <= date_from1`、`search_count >= search_n`、
  `search_mode and search_count > 0`、`sde.date > today + …`、
  `todo_days_value >= 0`、`sde.date == today: continue`、
  `not search_mode and …`、`deadline_date_str and not type_is_todo(...)`、
  `year and month and day`）は、**式も順序もそのまま**移しただけ

### 2. 旧コードとの応答の突き合わせ（GET 16 通り）

同じデータディレクトリの複製に対して、旧コード（`git stash` で戻したもの）と
新コードでサーバを起こし、同じ 16 個の GET を同じ順で投げて、
**応答 HTML 16 本と、できた `Conf.cgi` が全部バイト単位で一致**した
（`diff -r` が空）。投げたもの:

`date` のみ / `todo_days=1w` / `todo_days=`（空） / `filter_str=会議` /
`filter_str=`（空） / `search_str=会議` / `search_str=会議&search_n=1` /
`search_str=`（空） / `filter_str=!会議`（否定） / `filter_str=[`（不正な
正規表現） / `search_str=[`（同） / `year+month+day` / `cur_day` /
`todo_days=off` / `sde_align=bottom` / `search_str=NOTFOUND`（1 件も無い）

### 3. 旧コードとの突き合わせ（POST 7 通り）

同じく旧・新でサーバを起こし、`add`（通常）→ `add`（ToDo）→ `update` →
`fix`（別の日へ移動）→ **ToDo 完了（`deadline_*` 付き）** → `del` →
存在しない `sde_id` への `update` を同じ順で投げ、

- 応答 HTML 7 本
- できたファイルの一覧（`.bak` を含む）
- ファイルの中身（JSON Lines 全文）
- 最後の HTTP ステータス

を突き合わせて、**UUID を伏せれば全部一致**した。ToDo 完了で作られる
`〆2021/03/20 09:00-10:00\nmemo` と、補正後の `time_start`（`HH:MM`）まで
一致している。

### 4. 手元での動作確認

`--datadir` に一時ディレクトリを指定してサーバを起動し（**実データ
`~/ytsched/data` には一切触っていない**）、一覧・追加・ToDo・検索が
表示されることを確認。`ytsched x-data1` も動き、`finally` の
`_log.info("end")` が出ることを確認した。

## 単独で決めた判断

1. **`delta_day1` をクラス定数 `MainHandler.DELTA_DAY1` にした。**
   `get()` の中の `delta_day1 = datetime.timedelta(1)` は、
   `load_sched()` の中（ループの増減）と `render()` の引数の
   両方で要る。`load_sched()` の戻り値を 4 つにするか、同じ
   `datetime.timedelta(1)` を 2 か所に書くかの選択で、**値が固定の定数**
   なのでクラス定数にした。`timedelta` は immutable なので、
   使い回しても壊れない。テンプレート（`main.html` の
   `date_to - date_from + delta_day1`、`sde.html` の `delta_day1 * 7`）
   に渡る値は変わらない（上の 2 で HTML 一致を確認済み）
2. **`get_conf_arg()` の分岐を `value is not None and (empty_is_given or value)`
   の 1 行にした。** 「渡されたか」を先に `given` 変数へ入れる書き方だと、
   型チェッカが `value` を `str` に絞れず `str | None` を返すことになる。
   この形なら分岐の中で `str` に絞れて、`# type: ignore` も
   `assert` も要らない。読んでも 2 通りの条件が見える
3. **`empty_is_given` をキーワード専用引数（`*` の後ろ）にした。**
   呼び出し側に `empty_is_given=True` と必ず書かせるため。
   4 か所の食い違いが、呼び出しを見ただけで分かる
4. **`exec_cmd()` は `cmd` を自分で読む形にした**（`get()` から渡さない）。
   `cmd` は `exec_cmd()` の中でしか使わない
5. **`fix_todo_done()` の `"%H:%M"` を `SchedDataEnt.TIME_FORMAT` にした。**
   値は同じ。C で「`"%H:%M"` の直書きは `TIME_FORMAT` がある」と
   言われている件が、B の範囲にも 1 か所あったため揃えた
6. **`handler.py` の debug ログは 1 つの複数行 f-string にまとめた。**
   属性への代入 8 つは明示のまま（依頼どおり）
7. **`load_sched()` の引数は 9 個のまま、明示で渡した。**
   `self._filter_re` のようにリクエスト単位の属性へ持たせれば減らせるが、
   `filter_match()` の形（引数で受け取る）を変えることになり、
   「`filter_match()` に倣う」という依頼から外れる

## 気づいたが、直さずに残したもの

いずれも**挙動を変えないと直せない**ので、TODO-021 では触っていない。
implementer(1) の報告と同じものが多い。

1. **`search_n=`（空）で 500。**（A の範囲）`set_conf()` は先に済むので
   `Conf.cgi` に空の `SearchN` が残る。`get_conf_arg()` でも順序ごと保存した
2. **空の `filter_str` では保存済みの絞り込みが消えない。**（A の範囲）
   `empty_is_given=False` のため。`search_str` とは揃っていない
3. **`year`/`month`/`day` に数字でない値を渡すと 500。**（A の範囲）
   `get_date()` に移したが、検証は足していない
4. **`get()` はまだ 136 行ある。** うち 25 行は `render()` の引数で、
   残りも「設定値を 4 つ取り出して、集めて、描画する」という流れそのもの。
   これ以上分けると、かえって行ったり来たりが増えると判断した
5. **`load_sched()` の引数が 9 個。** 減らすにはリクエスト単位の状態を
   `self` へ持たせるか、まとめ役のデータ型を作ることになる。
   どちらも「挙動を変えない」範囲を超えて設計を動かすので見送った
6. **`MainHandler.COOKIE_TODO_DAYS` はどこからも使われていない。**
   （E の「意味の無い記述」に近いが、依頼の 4 項目に挙がっていないので
   残した）
7. **`sde_align` は `Conf.cgi` に保存されない。** 他の 4 つと違い、
   毎回既定値 `top` に戻る。仕様かどうか判断できないので触っていない

## うまくいかなかったところ

特に無い。途中でテストが落ちた段階も無かった（A〜E の各段階で 330 passed）。

一点だけ書いておくと、旧コードとの突き合わせは `git stash push -- src` →
旧コードで採取 → `git stash pop` の手順で行った。採取したデータは
一時ディレクトリ（scratchpad）に置いてあり、リポジトリには残していない。
