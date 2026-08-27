# TODO-079 implementer への依頼

`TODO.md` の TODO-079 と `docs/design-review.md` の F を先に読むこと。

**挙動は変えない。** HTML の出力が 1 バイトも変わらないのが正解。

## やること

### 1. 表示の条件を dataclass にまとめる

`src/ytsched/main_handler.py` に `@dataclasses.dataclass` を 1 つ足し、
`load_sched()` の引数のうち `date` 以外をまとめる。

- `filter_re` / `filter_neg` / `search_re` / `search_n` /
  `todo_days_value` / `todo_sde` / `todo_today_sde`
- `search_mode` は `search_re is not None` そのもの
  （`get()` の中でそう作っている）。フィールドにせず、プロパティにする
- `todo_by_date` も持たせる。**これがこの項目のもう一つの本題**で、
  いまは `load_sched()` が呼ばれるたびに `mk_todo_by_date()` が
  `todo_sde` を全件走査している。週の数（既定 9 週）だけ同じ集計を
  繰り返しているので、**dataclass を作るときに 1 回だけ作る**

置き場所は `main_handler.py` の中でよい（`MainHandler` の外、
モジュールの直下）。名前は英語で、既存の命名（`SchedDataEnt` など）と
釣り合うものにすること。

### 2. 呼び出しを直す

- `load_sched(date, cond)` の形にする
- `get()` の中の 2 か所（`sched, date_from, date_to = …` と、
  週ごとの繰り返しの中の `sched_offset, _, _ = …`）を直す
- `mk_todo_by_date()` は dataclass を作るところから 1 回だけ呼ぶ。
  メソッドのままでよいが、`self` をログにしか使っていないなら
  `@staticmethod` にしてよい（`search_match()` を使っているなら
  メソッドのまま）

### 3. docstring

`load_sched()` の Parameters を書き直す。dataclass 側にも、
何のためにまとめたか（TODO-079）を 2〜3 行で書く。

## 気をつけること

- **`load_todo()` は触らない。** 返り値をそのまま dataclass に入れるだけ
- 検索モードの分岐（`search_mode` で 1 週だけにする）は変えない
- `date_from` / `date_to` の返し方は変えない

## テスト

- `tests/test_main_handler.py` の `call_load_sched()`（857 行あたり）が
  `load_sched()` を直接呼んでいる。新しい形に合わせて直す。
  **テストの観点は変えない**
- 既存のテストが全部通ることが第一。新しいテストを足すなら、
  「`todo_by_date` が週の数だけ作り直されない」ことを見るものが 1 本
  あるとよい（`mk_todo_by_date()` の呼び出し回数を数えるなど）。
  難しければ省いてよい。報告に書くこと
- `tests/test_web.py` の HTML を見るテストが全部通ることで、
  「挙動が変わっていない」ことを確かめる

`mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
**`mise run upgradeproject` は走らせないこと。**
アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する。
