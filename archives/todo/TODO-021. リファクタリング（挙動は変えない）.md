# TODO-021. リファクタリング（挙動は変えない）

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort high、担当 = implementer × 2 + verifier + reviewer + runner

## きっかけ

TODO-020 まででデータ形式の移行が済み、`main_handler.py` の `get()` が
約 250 行に育っていた。設定値の取り出し・日付の決定・ToDo の読み込み・
一覧の収集・render が 1 つのメソッドに同居していて、どこを読めばよいかが
分からない。**挙動は一切変えない**のが前提。

## やったこと

### ゴールデンマスターテストを先に足した（290 → 330 件）

いまの挙動をそのまま書き留めておくテストを、手を付ける前に 40 件足した
（`tests/test_main_handler.py` 新規 39 件、`tests/test_handler.py` に 1 件）。
押さえたのは 5 つ。

1. 設定値の取り出し 4 か所の条件の食い違い
2. 検索モードの打ち切り条件
3. `exec_update()` の ToDo 完了時の補正
4. 日付の決定順
5. ToDo の表示条件

**足したテストが本当に効くかを、`src/` を一時的に 16 通り書き換えて
確かめた**（`>=` → `>`、`is not None` → truthy、`and` → `or` など）。
16 通りすべてで、新しいテストのどれかが落ちた。書き換えたあとは
`git status --porcelain src` が空であることを確認して元に戻している。

### A. `MainHandler.get()` の分割（約 250 行 → 136 行）

メソッドを 10 個切り出した。`get_conf_arg()` / `exec_cmd()` /
`get_modified_sde()` / `get_date()` / `get_sde_align()` /
`compile_filter()` / `compile_search()` / `load_todo()` / `load_sched()` /
`search_match()`。

**設定値の取り出し 4 か所は、条件を揃えずにまとめた。**

```python
if value is not None and (empty_is_given or value):
```

`empty_is_given=True` で `value is not None`（`search_str` / `search_n`）、
`False` で `bool(value)`（`todo_days` / `filter_str`）。
キーワード専用引数にしてあるので、呼び出しを見るだけで食い違いが分かる。
`.lower()` と `int()` は呼び出し側に残し、`set_conf()` がその前に来る
順序もそのまま（空の `search_n` は今までどおり 500 になり、
`SearchN` の保存だけ先に済む）。

### B. `exec_update()` の分割（約 130 行 → 95 行）

`get_date_arg()` / `get_time_arg()` / `get_deadline_str()` /
`fix_todo_done()` を切り出した。`fix_todo_done()` は 4 つ受け取って
4 つ返す形にし、新しいデータ型は作っていない。`cmd_add()` の位置引数
8 つの並びは変えていない（ゴールデンマスターテストがこれに依存している）。

### C. `ytsched.py`

`title_starts_with()` を足して `is_important()` / `is_canceled()` を
そこへ委譲、`is_todo()` を `type_is_todo()` へ委譲、`get_timestr()` を
`time2str()` を使う形へ、`load()` の中間変数を削除。

### D. `handler.py`

`get_conf()` の `try` / `except KeyError` を `dict.get()` へ。
`__init__` の 8 つの代入は**明示のまま残し**、1 行ごとに付いていた
debug ログだけを 1 つにまとめた（`setattr` やループにすると
basedpyright / mypy が属性を追えなくなる）。

### E. 意味の無い記述

`else: pass` 4 か所（A-1 でまとめた時点で消えた）、
空の `DataFileApp.end()` と `x_data1()` の `app.end()`。
`try` / `finally` は残した（例外が出たときの `_log.info("end")` の
出方を変えないため）。

## テスト

- **330 passed。着手時と同じ件数で、既存のテストは 1 行も書き換えていない**
- ruff format / ruff check / basedpyright（0 errors）/ mypy（Success）
- **旧コードとの突き合わせ。** `git stash` で旧コードに戻してサーバを
  起こし、新旧に同じ GET 16 通り・POST 7 通りを同じ順で投げて、
  応答 HTML・`Conf.cgi`・データファイルの中身が（UUID を除き）
  バイト単位で一致することを確認した。不正な正規表現、ToDo 完了、
  存在しない `sde_id` への `update` も含む
- verifier が実際にアプリを起動し、フィルタ・検索・不正な正規表現・
  `year`/`month`/`day`・add → fix → del・ToDo の追加と完了を叩いて、
  例外が出ないことを確認

## reviewer の指摘と、その扱い

### 直したもの — `is_todo()` の委譲で debug ログが増えた

元の `is_todo()` は `# self.__log.debug("")` と意図的にコメントアウト
されていたが、委譲先の `type_is_todo()` にはログが生きていた。
`sde.html` は 1 件につき最大 5 回 `is_todo()` を呼ぶので、100 件の一覧で
1 リクエスト数百行になる。f-string の組み立ては水準に関係なく走るので、
既定の INFO でも費用だけかかる。

**`type_is_todo()` 側の debug を落とした。** 放置も「0 行 → 数百行」の
変化なので、どちらかは動かす必要がある。`is_important()` /
`is_canceled()` / `is_holiday()` はどれもログを出しておらず、元の
`is_todo()` も黙っていたので、こちらに揃えるほうが小さい。

### 残したもの

- **`fix_todo_done()` の `"%H:%M"` → `TIME_FORMAT`** — C の指摘を B の
  範囲へ広げた「ついでに揃えた」1 件だが、値が同一で挙動に差が無く、
  これで `"%H:%M"` の直書きが `src/` から消えた
- `load_sched()` の引数 9 個、`exec_cmd()` が描画も担っていること、
  `title_starts_with()` が毎回 `tuple()` を作ること — いずれも
  「挙動を変えない」範囲を超えるか、実害が無い

## 見つけたが直さなかった挙動（別項目の候補）

TODO-021 は挙動を変えない項目なので、**現状のままテストに書き留めてある**。

1. **`search_n=`（空）で 500。** `int("")` が `ValueError`。しかも
   `set_conf()` は先に済むので、`Conf.cgi` に空の `SearchN` が残る
   （次のリクエストでは既定値へ落ちて画面は直る）
2. **空の `filter_str` では保存済みの絞り込みを解除できない。**
   `search_str` は空で送れば消えるのに、`filter_str` は消えない
3. `detail` の `〆` 行に余分な空白が残ることがある（時刻が両方空のとき）
4. `Conf.cgi` には `ABC` のまま保存され、画面には `abc` と出る
   （`set_conf()` が `.lower()` より前）
5. 検索モードで 1 件も当たらないと 1825 日ぶんスキャンする（速度の話）
6. `year` / `month` / `day` に数字でない値や `day=0` を渡すと 500
7. `MainHandler.COOKIE_TODO_DAYS` がどこからも使われていない
8. `sde_align` だけ `Conf.cgi` に保存されず、毎回既定値 `top` に戻る

## 担当の分け方

分担の理由と各担当の報告は `archives/agents/TODO-021/` にある。

**implementer を 2 人に分けたのが効いた。**
ゴールデンマスターテストを書く担当と、
リファクタリングする担当を分けないと、「これから変えるつもりの形」に
合わせたテストになりかねない。分けた結果、テストを 1 行も書き換えずに
済んでいる。

**runner を初めて使った**（TODO-022 で作った定義）。最終確認の 5 コマンドを
34 秒・18k トークンで走らせた。同じ範囲を verifier に見せると
4 分半・64k かかっている。決まった手順を流すだけなら runner で足りる。
