# TODO-021 implementer(2) への依頼 — リファクタリング本体

## 大前提

**挙動を一切変えない。** これが TODO-021 の唯一の前提。

- **既存のテストを書き換えない。** 1 文字も。書き換えが要ると感じたら、
  それは**挙動が変わった印**なので、そこで手を止めて報告する
- テストは全件通っている状態から始める（件数は着手時に自分で確認する）。
  終わったときも**同じ件数が全部通る**こと
- 別の担当が「現状の挙動を押さえるテスト」を先に足してある
  （`archives/agents/TODO-021/implementer1-report.md` に一覧がある）。
  **先にその報告を読むこと。** 何が固定されているかが分かる

## やること

`TODO.md` の TODO-021 の A〜E。以下は補足で、細部の形は任せる。

### A. `MainHandler.get()` の分割

1. **設定値の取り出し 4 か所を 1 つにまとめる**
   （`search_str` / `todo_days` / `filter_str` / `search_n`）。
   共通の形はこう:

   ```
   value = self.get_argument(arg_name, None)
   if <渡されたか>:
       if value != conf_value:
           self.set_conf(conf_key, value)
   elif conf_value:
       value = conf_value
   else:
       value = default
   ```

   **`<渡されたか>` だけが揃っていない。**
   `search_str` と `search_n` は `value is not None`、
   `todo_days` と `filter_str` は `bool(value)`。
   これは**空文字を渡したときの挙動の違い**なので、
   **引数で残す**（揃えない）。揃えたくなったら別の TODO 項目にする。

   `filter_str` だけ `get_argument("filter_str", "")` と既定値が
   `""` になっているが、truthy で分岐するので `None` と等価。
   まとめてよい。

   `.lower()` と `int()` は呼び出し側に残す（値ごとに違うため）。

2. **`search_re` によるマッチ 3 か所を、`filter_match()` と同じ形の
   メソッドにする。** 今はこう散っている:

   ```
   if search_re is not None and not search_re.search(sde.search_str()):
       continue
   ```

   `filter_match()` に倣って `search_match(search_re, sde) -> bool` を
   作り、`if not self.search_match(...): continue` にする。
   `search_re is None` のときは `True`（＝絞り込まない）。

3. **ブロックごとにメソッドへ切り出す。**
   `get()` の中のコメント（`# set Date`、`# load ToDo`、
   `# load schedule data` など）が、そのまま切り出しの単位になっている。

   注意する点:
   - `cmd` のブロックは、`cmd == "update"` のときに **`render()` して
     `return` する**。切り出すなら「描画したかどうか」を返して、
     `get()` 側で `return` する形になる
   - 一覧を集めるブロックは、ループの中で `date_from` を書き換える。
     `date_from` は最後の `render()` にも渡っているので、
     **切り出したメソッドから返す**必要がある
   - `delta_day1` も `render()` に渡っている

### B. `exec_update()` の分割

- フォーム引数の取り出しと、**ToDo が完了したときの
  `date` / `time_start` / `time_end` / `detail` の補正**を分ける
- 補正のブロックは、`deadline_date` があって、かつ `sde_type` が
  ToDo でないときだけ走る。この条件は変えない
- 9 個の値を返すためだけに新しいデータ型を作らない。
  素直に読める形（補正だけを別メソッドにして、
  4 つの値を受け取って 4 つ返す等）でよい

### C. `ytsched.py`

- `is_important()` と `is_canceled()` は、
  「`title` を `normalize()` して、リストのどれかで始まるか」で同じ。
  共通のヘルパにまとめる。
  先頭の `if self.title == "": return False` は、
  空文字ならどの接頭辞にも一致しないので落としてよい
  （**接頭辞のリストに空文字が無いことを確かめてから**落とすこと）
- `is_todo()` は `type_is_todo(self.type)` へ委譲する
- `SchedDataFile.load()` の `out2 = sorted(...); return out2` の中間変数
- `get_timestr()` の冗長さ。`"%H:%M"` の直書きは `TIME_FORMAT` がある

### D. `handler.py`

- `get_conf()` の `try` / `except KeyError` は `self._conf.get(name)` で済む
- `__init__` の `app.settings.get()` の繰り返し。
  **ただし属性への代入は明示のまま残す**
  （`setattr` やループにすると basedpyright / mypy が属性を追えなくなり、
  サブクラスでの `self._title` などが型エラーになる）。
  繰り返しているのは**代入 1 行ごとに付いている debug ログ**のほうなので、
  そちらを 1 つにまとめる

### E. 意味の無い記述

- `main_handler.py` の `else: pass` が 4 か所（設定値の取り出しにある。
  A-1 でまとめれば自然に消えるはず）
- `__main__.py` の `DataFileApp.end()` が空。メソッドと、
  `x_data1()` の中の `app.end()` の呼び出しを消す。
  **`try` / `finally` は残す**（例外が出たときに `_log.info("end")` が
  出るかどうかが変わってしまうため）

## 気をつけること

- **範囲を広げない。** A〜E の外は直さない。気づいたことは報告に書く
- **「ついでに揃える」をしない。** 揃っていない条件は、
  揃っていないまま残すのが今回の仕事
- 各段階で `uv run pytest tests` を走らせ、**どこで壊れたかが分かる形で
  進める**（A を全部やってから初めて走らせる、をしない）
- lint・型チェックまで通す:
  `uv run ruff format --line-length 78 src tests` /
  `uv run ruff check --fix --extend-select I src tests` /
  `uv run basedpyright src tests` / `uv run mypy src tests` /
  `uv run pytest tests`
- 行長は 78

## 報告

`archives/agents/TODO-021/implementer2-report.md` に書く。

- A〜E ごとに、何をどう変えたか（ファイル・メソッド名。全文は貼らない）
- **挙動が変わっていないと言える根拠**（テスト件数と結果、
  条件式をどう保存したか）
- **判断に迷った点**と、どちらを選んだか・その理由
- やらずに残したものと、その理由
- 気づいたが直さなかったもの（どの TODO 項目の範囲か添える）

---

## 追記（main より。implementer(1) の結果を受けて）

### ゴールデンマスターテストは 330 件

`290 → 330`（+40 件）。`tests/test_main_handler.py`（新規 39 件）と
`tests/test_handler.py`（1 件追記）。**着手前に
`archives/agents/TODO-021/implementer1-report.md` を必ず読むこと。**
何がどう固定されているかの一覧がある。

implementer(1) は、`src/` を一時的に 16 通り書き換えて
「足したテストが実際に落ちる」ことまで確かめている。
**条件式をうっかりずらせば、必ずどれかが落ちる。**

### `cmd_add()` の引数の並びを変えないこと

`test_deadline_fixes_date_and_time_start` が
`MainHandler.cmd_add` を `mock.patch.object` で包んで、
**位置引数 8 つ**（`sde_id, date, time_start, time_end, sde_type,
title, place, detail`）を見ている。

implementer(1) の報告には「並びを変えるならテストを直してよい」と
あるが、**main の判断としては変えない**。`cmd_add()` は TODO-021 の
A〜E の範囲外だし、「テストは 1 行も書き換えない」を崩したくない。
`exec_update()` の分割は、`cmd_add()` の呼び出し口をそのままに行うこと。

### 見つかっている不具合は直さない

implementer(1) が 6 件の「おかしそうな挙動」を報告しているが、
**どれも直さない**（TODO-021 は挙動を変えない項目）。
現状の挙動としてテストに書き留めてあるので、**そのまま通ること**が
リファクタリングが正しいことの根拠になる。とくに:

- `search_n=`（空）は `int("")` で **500 になる**。しかも
  `set_conf()` は先に済んでいる。**この順序も変えない**
- 空の `filter_str` では保存済みの絞り込みが消えない
- `set_conf()` は `.lower()` の**前**にある。この順序も変えない
