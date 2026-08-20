# TODO-021 implementer(1) への依頼 — 現状の挙動を押さえるテスト

## あなたがやること

**テストを足すだけ。`src/` には一切手を触れない。**

TODO-021 はリファクタリング項目で、**挙動を一切変えない**のが前提。
そこで、いま動いているコードの挙動をそのまま書き留めておく
ゴールデンマスターテストを先に足す。リファクタリング本体は**別の担当**が行うので、あなたは
「これから変えるつもりの形」を想像せずに、**いまの挙動をそのまま**
書き留めること。

## 前提

- ベースラインは `uv run pytest tests` で **290 passed**（main が確認済み）
- 既存のテストは**書き換えない**。足すだけ
- テストの置き場所は既存に合わせる（`tests/test_web.py`,
  `tests/test_ytsched.py`, `tests/test_handler.py`）。新しいファイルを
  作るかどうかは、既存の粒度を見て判断してよい

## 押さえてほしい挙動

`src/ytsched/main_handler.py` の `MainHandler.get()` と `exec_update()`、
`src/ytsched/handler.py`、`src/ytsched/ytsched.py` のうち、
**これから分割・整理される部分**。とくに次の 5 つ。

### 1. 設定値の取り出し 4 か所の、条件の食い違い

`search_str` / `todo_days` / `filter_str` / `search_n` の 4 か所は、
似た形に見えて条件が揃っていない。

- `search_str` と `search_n` は `is not None` で分岐する
  （＝空文字を渡すと「渡された」扱いになり、`Conf.cgi` に保存され得る）
- `todo_days` と `filter_str` は truthy で分岐する
  （＝空文字を渡すと「渡されていない」扱いになり、`Conf.cgi` の値か
  既定値へ落ちる）

**この差が、空文字を渡したときに外から観測できる形でテストにしてほしい。**
観測点は「`Conf.cgi` の中身がどうなるか」と「返る HTML／画面の状態」。
`search_str=` と `filter_str=` を空で送ったときに、`Conf.cgi` の
`SearchStr` / `FilterStr` がどうなるかを、それぞれ別のテストにする。

### 2. 検索モードの打ち切り条件

`get()` の `while date1 > date_from:` のループ。

- `search_mode` は「文字列が空でないか」ではなく
  「**正規表現としてコンパイルできたか**」で決まる（TODO-012）
- 検索モードのとき、`search_count >= search_n` で打ち切る
- `date1 <= date_from1`（`SEARCH_MODE_DAYS` = 365 日）でも打ち切る
- 検索モードでない範囲は `self._days` の前後

`search_n` を小さくしたときに、何件で打ち切られるかが分かるテストが要る。
テストデータの日付は、`self._days`（既定 45）や 365 日の境界を
またぐように置くこと。

### 3. `exec_update()` の ToDo 完了時の補正

`deadline_date` が渡され、かつ `sde_type` が ToDo **でない**とき、
`date` が今日に、`time_start` が現在時刻（秒以下を切り捨て）に
書き換えられ、`detail` の先頭へ `〆{日付} {開始}-{終了}` の 1 行が
足される。`time_end` は `None` になる。

**この補正が「起きる条件」と「起きない条件」の両方**を押さえる。
現在時刻に依存するので、`freezegun` のような外部依存を足さずに
（`monkeypatch` で十分）書けるか見てほしい。書けないなら、
時刻そのものではなく「秒以下が落ちていること」「`detail` の先頭行の形」
のように、時刻に依存しない性質でもよい。

### 4. 日付の決定順

`get()` の「set Date」ブロック。`cur_day` / `date` / `year`+`month`+`day` /
`modified_date` のどれが勝つか。とくに:

- `year` `month` `day` が 3 つ揃ったときだけ効く（1 つでも欠けると無視）
- `modified_date` は `date` 引数より後に上書きする
- どれも無ければ `cur_day`、`cur_day` も無ければ今日

### 5. ToDo の表示条件

`todo_days_value >= 0` の分岐、`todo_today_sde` に入る条件
（`sde.date > today + todo_days_value` なら入らない、
`sde.date == today` なら入らない）、
検索モードのときは `todo_today_sde` を混ぜない（`not search_mode`）。

## 気をつけること

- **`src/` を編集しない。** テストを書いていて「ここはバグでは」と
  思ったら、直さずに報告へ書く（TODO-021 は挙動を変えない項目なので、
  バグが見つかっても別項目になる）
- **テストが今のコードで通ることを、実際に走らせて確かめる。**
  通らないテストを残さない。「こうあるべき」ではなく
  「**いまこう動く**」を書く。もし「これは明らかにおかしい挙動だ」と
  思っても、いまの挙動どおりにテストを書き、おかしいと思った点は報告へ
- 既存のテスト（`tests/test_web.py` など）に**同じ内容が既にある**なら、
  重複させない。先に読んで確かめる
- テストの名前と docstring で、**何を押さえているのか**が分かるようにする。
  「リファクタリングでこれが壊れたら挙動が変わった印」という位置づけが
  伝わるコメントを添える
- 外部依存（`freezegun` など）を足さない
- lint・型チェックまで通す:
  `uv run ruff format --line-length 78 src tests` /
  `uv run ruff check --fix --extend-select I src tests` /
  `uv run basedpyright src tests` / `uv run mypy src tests` /
  `uv run pytest tests`

## 報告

`archives/agents/TODO-021/implementer1-report.md` に書く。

- 足したテストの一覧（ファイル・テスト名・何を押さえているか）
- **押さえられなかったもの**と、その理由（あれば）
- テストを書いていて気づいた、挙動がおかしそうな点（直さずに報告）
- 最終的なテスト件数（`290` から何件増えたか）
