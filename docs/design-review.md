# 基本設計のレビュー（2 回目・2026-08-27）

`src/ytsched/` 全 11 ファイル（3,704 行）、テンプレート 4 つ、
`static/js/` の 8 本（1,563 行）を読み、モジュールの分け方とクラスの
持ち方について挙げたもの。

**これは現行仕様ではない。** 「こう直したい」と考えたことの記録で、
実際に何をどう直したかは各 TODO 項目の `archives/todo/` 側にある。

2026-08-28 に、A〜P の 16 件を 9 項目にまとめて立てた。

| 項目 | 中身 |
|---|---|
| TODO-087 | A |
| TODO-088 | B |
| TODO-089 | M |
| TODO-090 | C・D・E・F と、P の `webapp.py` の件 |
| TODO-091 | G・H |
| TODO-092 | I・J・K・L |
| TODO-093 | N・O |
| TODO-094 | P のうち直すもの |
| TODO-095 | P のうち ruff の規則（決めるだけの項目） |

C・F と `webapp.py` の件を TODO-090 に寄せたのは、D・E と同じ
「設定とキャッシュを、どこが持ってどう書くか」の話で、別々に直すと
同じ場所を 2 度触ることになるため。

1 回目のレビュー（TODO-077〜083 のもと。同じファイルにあった A〜K）は
すべて決着したので、この文書ごと書き直した。中身は git の履歴にある。

決着済みの項目（`archives/todo/`）を読んだうえで挙げているので、一度
「やらない」と決めたものは入っていない。**1 回目で「あとで考え直す」と
して持ち越したものは、A と M として再掲している。**

## 全体

1 回目のあと 7 項目が入り、直したいと書いたことはおおむね直っている。
データが失われる経路は、今回は見つからなかった（1 回目の B は
TODO-077 で直り、外部の変更に追随しない件も TODO-080 で直っている）。

以下は**構成とクラスの持ち方に絞った**指摘で、多くは「片方だけ直った」
「決めたことが 1 か所だけ守られていない」という形をしている。

---

## A. `MainHandler` が 1,391 行のまま、3 つの役割を抱えている

TODO-077 が「`exec_update()` 一式の置き場所は、TODO-081 のあとで考え
直す」として持ち越した件。TODO-081 は済んだので、いまが考え直すとき。

中身を数えると、3 つがほぼ同じ大きさで並んでいる。

| 役割 | メソッド | 行数 |
|---|---|---:|
| 更新の実行 | `post()` `exec_cmd()` `get_modified_sde()` `exec_update()` `get_date_arg()` `get_time_arg()` `get_deadline_str()` `fix_todo_done()` `cmd_add()` `cmd_del()` | 約 490 |
| 一覧の組み立て | `get()` `load_todo()` `mk_todo_by_date()` `load_sched()` `compile_*()` `*_match()` | 約 510 |
| 引数と設定値の変換・検証 | `get_conf_arg()` `get_date()` `ymd2date()` `str2*()` `get_load_months()` `months2weeks()` `mkurl()` | 約 300 |

`ytsched.py`（950 行）に対しても、`edit_handler.py`（143 行）に対しても
突出している。

**案:** 更新の実行を、`SchedData` とフォームの値を受け取るクラス
（`main_handler.py` から出す）へ移す。TODO-077 が「フォームの値の取り出しが
`get_argument()` に依存している」として挙げていた点は、
`get_date_arg()` / `get_time_arg()` / `get_deadline_str()` がハンドラ側で
値を取り出して 1 つの dataclass に詰め、それを渡す形にすれば消える。
`cmd_add()` / `cmd_del()` / `fix_todo_done()` は tornado を知らずに済む。

## B. 一覧の組み立てが、週の表示と検索を 1 つのループでやっている

`load_sched()`（112 行）は、通常モードでは「月曜から 7 日ぶんを並べる」、
検索モードでは「最大 1,825 日さかのぼって、当たった日だけ残す」という
別々のことを、同じ `while` の中で分岐しながらやっている。

`search_mode` の分岐は、`get()` に 1 か所、`load_sched()` に 4 か所ある。
さらにテンプレート（週バーを出すか、日付の欄を押したときの動き）と
ブラウザ側（`data-monday` が付かない、`gauge_r` が無い）にも同じ前提が
散っている。**検索は実質もう 1 つの画面**なのに、1 つのハンドラと
1 つのテンプレートが分岐で抱えている。

`get()` が 175 行あるのも、この分岐と、引数 7 種の取り出しと、週の
繰り返しと、21 個の値を渡す `render()` が 1 つのメソッドに同居して
いるため。

**案:** 「1 週ぶんを組み立てる」関数と「検索結果を集める」関数に分ける。
`SchedLoadCond`（TODO-079）のうち `search_re` / `search_n` は検索側だけの
持ち物になり、通常モードの条件は 4 つに減る。

## C. `post()` と `get()` が、同じ 4 つの変換を並べている

`search_str` / `filter_str` / `todo_days` / `search_n` の
`get_conf_arg()` 呼び出しが、`post()` と `get()` にそっくり同じ形で
並んでいる。`post()` の 3 つは戻り値を使わず `_ =` で捨てていて、
**「読むと `conf.json` へ保存される」という副作用のためだけに呼んで
いる**（docstring にもそう書いてある）。

`get_conf_arg()` は名前が `get_` で始まるのに `set_conf()` を呼ぶ。

**案:** 「リクエストの値を `conf.json` へ取り込む」メソッドを 1 つにして、
`post()` と `get()` の両方から呼ぶ。名前も、読むだけでないことが分かる
ものにする。

## D. 依存の渡し方が、`sd` だけ直っている

TODO-081 で `SchedData` は `initialize()` で受け取る形になったが、
`title` / `author` / `version` / `url_prefix` / `datadir` の 5 つは
`app.settings.get()` のままで、型はどれも `Any`。

`self._datadir` は `os.path.join(self._datadir, self.CONF_FNAME)` に
渡るので、設定が欠けていれば `TypeError` になる。型チェッカは何も
言わない。

**案:** 5 つも `initialize()` の引数にするか、まとめて 1 つの dataclass
（アプリの設定）にして渡す。`webapp.py` の URL 登録 5 行が
`{"sd": ..., "conf": ...}` になる。

## E. `conf.json` の扱いが、データファイルと食い違っている

同じ「読んで書くファイル」なのに、2 つの答えが並んでいる。

| | データファイル（`.jsonl`） | `conf.json` |
|---|---|---|
| 読み込み | キャッシュし、`mtime`+`size` で読み直す（TODO-080） | リクエストのたびに読む |
| 書き込み | 変更を覚えて、最後に 1 回（TODO-077） | `set_conf()` のたびに全体を書く |

`get()` で 4 つの設定値が同時に変われば、`conf.json` を 4 回書く。
TODO-077 で `.bak` の件を直したときの理由（1 回の更新で同じファイルを
何度も書かない）は、こちらにもそのまま当てはまる。

**案:** `conf.json` も同じ形にする。読み込みは `SchedData` と同じく
キャッシュ + 変更の検出、書き込みは 1 リクエストにつき 1 回にまとめる。
なお `.bak` は取っていないので、失われるデータは無い。

## F. キャッシュの読み直しが、覚えている変更を見ていない

`SchedData.get_sdf()` は、ファイルが外部で書き換わっていれば
`SchedDataFile` を**作り直す**（TODO-080）。一方 `_dirty_sdf` は、
変更のあった `SchedDataFile` の**インスタンスそのもの**を覚えている
（TODO-077。日付で覚えると、キャッシュから捨てられたときに変更が消える
ため）。

1 リクエストの中で同じ日を 2 回引き、その間に外部がそのファイルを
書き換えると、`_dirty_sdf` には古いインスタンスが残ったままになり、
`save()` がそちらを書いて、読み直した内容を消す。**単一ユーザなので
まず起きない**が、2 つの仕組みが互いを見ていないのは確か。

**案:** `get_sdf()` の読み直しで、`_dirty_sdf` に載っている日は
読み直さないと決めて、そう書く（未保存の変更を優先する）。
1 行で済み、なぜそうなのかがコードに残る。

## G. テンプレートに `SchedData` そのものを渡している

`main.html` の

```html
Version {{ version }}
<span class="my-fs-xx-small">({{ sd.get_cache_size() }})</span>
```

のために、`MainHandler.get()` が `sd=self._sd` を `render()` へ渡して
いる。**データを持つオブジェクトが、そのままテンプレートに入る唯一の
経路**で、テンプレートからは `sd` のどのメソッドも呼べる。

`get_cache_size()` の呼び出しは、`src/` の中では他に、`get_sdf()` が
キャッシュの上限と比べるところが 1 か所あるだけ。

**案:** 数だけ渡す（`cache_size=self._sd.get_cache_size()`）。
そもそも画面に出し続けるかどうかも、決め直してよい。

## H. 表示に渡す値が、`list[dict]` のまま

入力側の条件は TODO-079 で `SchedLoadCond` という dataclass になったが、
出力側は dict のまま残っている。

- `load_sched()` が返す `sched` は `list[dict]`（`date` / `is_holiday` /
  `sde` の 3 キー）
- `get()` が作る `weeks` は `list[dict[str, object]]`。検索モードでは
  `monday` が `None` になるので、**型を揃えられずに `object` で受けて
  いる**（コードにもそう書いてある）

テンプレート側は `sched_ent['date']`、`w['monday']` と文字列で引くので、
キー名を変えても型チェッカは気づかない。

**案:** 1 日ぶんと 1 週ぶんの dataclass を 2 つ作る。`monday` が
`None` になるのは B（検索を分ける）と一緒に片付く。

## I. テンプレートが、呼び出し元の変数に暗黙に依存している

`{% include sde.html %}` は名前空間を共有するので、`sde.html` は
`main.html` 側の `{% set %}` と `render()` の引数を、宣言なしにそのまま
使っている。実際に使っているのは 10 個。

```
sde  sched_date  today  today_flag  delta_day1  date  date_from  date_to
url_prefix  sde_count
```

どれが要るかは `sde.html` を全部読まないと分からず、`main.html` 側で
`{% set %}` の位置を動かすと黙って壊れる。

**案:** ファイルの先頭に、使う変数をコメントで並べる。
（`{% module %}` へ移すのは、値の渡し方が変わって大きくなるので、
今回の範囲では勧めない。）

## J. ToDo の色分けの判定が、テンプレートの中にある

`sde.html` の先頭で、期限の近さを見て class を選んでいる。

```
{% if sde.date < today %}                      → my-sde-todo-over
{% elif sde.date <= today + delta_day1 * 7 %}  → my-sde-todo-near
```

**「1 週間以内」の 7 がテンプレートに直接書いてある。**
`is_todo()` / `is_important()` / `is_canceled()` / `is_holiday()` は
`SchedDataEnt` にあるのに、この 2 つだけ判定の置き場所が違う。

**案:** `SchedDataEnt` に寄せる（今日を受け取るメソッドを 2 つ足す）。
日数も、そのクラスの定数になる。

## K. どこからも読まれない hidden input・クエリ・変数

テストが固定しているわけではないので、消せば消える。

- `main.html:77` の `cur_day` — `id` が無く、どのフォームの中にも
  無い。JavaScript は `getElementById("cur_day")` で**別の**（312 行の）
  input を引いている。送信もされない
- `main.html:79` の `search_n` — 同じくフォームの外。目標件数を送るのは
  `changeSearchN()`（`search_n_in` の `select`）のほう
- `sde.html:83-85` — 編集画面へ `cur_date` / `date_from` / `date_to` を
  渡しているが、`EditHandler` はどれも読まない。TODO-050 で
  「URL に持たせるのは日付だけ」と決めたのに、ここだけ 6 個載っている
- `sde_count` — `main.html` で 0 にして `sde.html` で 1 ずつ増やすが、
  どこにも出さない
- `base.html:2` の `now` — 描くたびに `datetime.now()` を呼ぶが、使わない

## L. `year` / `month` / `day` の 3 引数を送る画面が、もう無い

`get_date()` の**優先順位が一番強い**経路（`year`+`month`+`day`）と、
そのための `ymd2date()` / `str2ymd_date()` は、テンプレートにも
`static/js/` にも呼び出しが無い。叩いているのは `test_web.py` と
`test_main_handler.py` だけ。

TODO-050 で日付は `date=YYYY-mm-dd` に一本化されたので、旧 CGI 時代の
入口が残っている形。1 回目の J（使われていない属性をテストが固定して
いる）と同じで、**テストがあるので使われているように見える**。

**案:** 手で URL を叩くための入口として残すなら docstring にそう書く。
消すなら、テストと、`str2ymd_date()` の中の `check_int_range()` 3 つも
一緒に消す（関数そのものは `str2todo_days()` などが使う）。

## M. `edit.html` に 100 行の `<script>` が残っている

TODO-083 が「範囲外」として持ち越した件。`main.html` の 120 行は
`main-page.js` へ出たが、`edit.html` はそのまま。

- `onloadHdr()` が `main-page.js` にも `edit.html` にもある。**同じ名前で
  中身が違う**（読み込まれるページが違うので衝突はしない）
- `submitCmd()` / `changeElDate()` / `changeDetailHeight()` は
  テンプレートの値を使っていないので、そのまま外へ出せる
- 使われていないものが混ざっている（`resize` のリスナーはコメント
  アウト、`rotationchange` はそういうイベント名が無い）

**案:** `edit-page.js` を作り、`main-page.js` と同じ形にする
（テンプレートの値だけ `<script>` に残す）。

## N. ブラウザ側の状態が、`ytState` と hidden input に分かれている

TODO-083 で「ファイルをまたぐ状態は `ytState` に集める」と決めたが、
集めたのは要素の参照 4 つと `activeWeekOffset` だけ。**いま見ている
日付は DOM の hidden input が持っている。**

`setActiveWeek()` が `cur_day` / `date` / `date_from` の 3 つの
`value` を書いて揃え、`moveToMonday()` は `#cur_day` を読み、
`onloadHdr()` は `#date_from` を読んでゲージを合わせる。
「いまどの週にいるか」を知るのに 2 つの置き場所を見ることになる。

**案:** 日付も `ytState` に持ち、hidden input は**フォームで送るときに
書く**ものと割り切る。`#date_from` は、ゲージのために値を渡している
だけなので `data-*` 属性で足りる。

## O. JavaScript のファイル間の依存が、読み込み順にしか書かれていない

ES モジュールにしないと決めた（TODO-083）ので `import` は書けないが、
実際の依存はある。

| 呼ぶ側 | 呼ばれる側 |
|---|---|
| `swipe.js` | `url_prefix`（`base.html` の `<script>`） |
| `main-page.js` | `search_str0` / `today_str`（`main.html` の `<script>`） |
| `gauge.js` | `nav.js` の `shiftDays()` / `calcDays()` / `getLocaltimeDateString()` |
| `week.js` | `gauge.js` の `mondayOf()` / `dispGauge()`、`nav.js` の `scrollToId()` |
| `swipe.js` | `week.js` の `moveToMonday()` / `slideWeekWrap()` |

`base.html` の `<script>` の並びがそのまま仕様になっていて、順番を
入れ替えても**読み込み時には何も起きず、押したときに初めて壊れる**。

**案:** 各ファイルの先頭に「外から使うもの」をコメントで並べる。
`src/README.md` の表に依存の列を足すのでもよい。

## P. 細かいもの

- ruff は既定の規則（`E4,E7,E9,F`）に `I` が乗っただけ。TODO-082 は
  置き場所を `pyproject.toml` へ移しただけで、**規則を増やすかどうかは
  決めていない**。`B`（bugbear）や `SIM` を足すかは、決めるだけの項目
- `SEARCH_MODE_DAYS`（365）が `MainHandler`、`SEARCH_MODE_MAX_DAYS`
  （1,825）が `handler_util`。名前が似ていて意味が違う（前者は 1 件も
  当たらないときに諦める日数、後者は絶対の上限）
- `webapp.py` の URL 登録で `{"sd": self._sd}` が 5 回並ぶ。D で
  渡すものが増えると、そのまま 5 か所に効く
- `mk_todo_by_date()` が `search_match()` をもう一度かけている。渡って
  くる `todo_sde` は `load_todo()` が同じ条件で絞ったあとのもの
- CLI のオプションで `--size_limit` だけアンダースコア（他は
  `--dry-run` / `--error-file`）

---

## 手を付ける順（レビュー時点の見立て）

| | 中身 | 効き | 手間 |
|---|---|---|---|
| 1 | **A**（更新の実行を分ける）| TODO-077 からの持ち越し | 大 |
| 2 | **B**（一覧と検索を分ける）| `get()` と `load_sched()` の両方が縮む | 中 |
| 3 | **M**（`edit.html` の JavaScript）| TODO-083 からの持ち越し | 小 |
| 4 | **D・E**（依存の渡し方、`conf.json`）| 片方だけ直っているのを揃える | 中 |
| 5 | **H・G**（dict と `sd` の渡し方）| テンプレートとの境目がはっきりする | 中 |
| 6 | **I・J・K・L**（テンプレートの掃除）| 読む前の見通し | 小 |
| 7 | **C・F・N・O・P** | 読みやすさ、次に触る人 | 小 |

着手する順番は利用者が決める。この表はレビューした時点での見立て。
