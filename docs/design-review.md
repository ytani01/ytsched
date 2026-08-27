# 基本設計のレビュー（2026-08-27）

`src/ytsched/` 全 9 ファイル（3,681 行）、テンプレート 4 つ、
`my.js`（1,358 行）を読み、モジュールの分け方とクラスの持ち方について
挙げたもの。個々の見出しの末尾に、対応する TODO 項目の番号を付けてある。

**これは現行仕様ではない。** 2026-08-27 時点で「こう直したい」と
考えたことの記録で、実際に何をどう直したかは各 TODO 項目の
`archives/todo/` 側にある。直し終わった項目の記述は、ここでは
古いまま残る。

決着済みの項目（`archives/todo/`）を読んだうえで挙げているので、
一度「やらない」と決めたものは入っていない。

## 全体

小さいアプリとしては、よく手入れされている。データ・Web・CLI・ログの
分かれ方は素直で、「なぜそうしたか」が docstring と TODO 番号で追える。
以下は**構成とクラスの持ち方に絞った**指摘で、データが失われるのは
B だけ。

---

## A. ゲージの計算が、サーバとブラウザに二重にある（TODO-078）

`main_handler.py` の `days2x_percent()` / `calc_gauge_label()` /
`DAYS_YEAR` / `DAYS_MONTH` / `DAYS_GAUGE_K` / `DAYS_GAUGE_MAX` と、
`my.js` の `days2xPercent()` / `gaugeDiffLabel()` / 同名の定数が、
同じ式・同じ数値をそれぞれ持っている。
`calc_gauge_label()` の docstring 自身が「食い違うと針が動く前後で
文字が変わって見える」と書いており、揃え続けるのは人の注意任せ。

**案:** サーバ側は「初回の描画に必要な値」だけをテンプレートへ渡す
（`GAUGE` の目盛りは今でもそう）。ラベルの文字を JavaScript だけの
持ち物にすれば、Python 側の `calc_gauge_label()` と定数 3 つが消える。
残すなら、少なくとも数値が一致することを見るテストを 1 本置く。

## B. `fix` すると `.bak` が「削除直後の中間状態」で上書きされる（TODO-077）

`exec_update()` は `fix` を **`cmd_del()` → `cmd_add()`** で実装していて、
`SchedData` の `del_sde()` / `add_sde()` はそれぞれ `sdf.save()` を呼ぶ。
同じ日のファイルが 1 回の修正で 2 回保存され、2 回目の `.bak` が
1 回目の結果（1 件消えた状態）を写す。

実際に確かめた（A・B の 2 件がある日で B を修正）:

| | 中身 |
|---|---|
| 修正前のファイル | 予定A, 予定B |
| 修正後の `.bak` | **予定A のみ** |

**修正前の内容がどこにも残らない。** バックアップとしては働いていない。

**案:** `SchedDataFile` の「変更」と「保存」を分け、1 リクエストで
保存を 1 回にする（`del` してから `add` し、最後に 1 回 `save()`）。
`SchedData.add_sde()`/`del_sde()` が保存まで抱えているのを解くのが要る。

## C. `SchedData` のキャッシュが、外部の変更に追随しない（TODO-080）

`_sdf_cache` は上限 20,000 件（LRU）で、実際にはまず捨てられない。
`mtime` を見ていないので、`ytsched migrate` や手でファイルを直しても、
そのプロセスが生きている間は古い内容を返し続ける。
ホームボタンのダブルタップは DOM を取り直すだけで、サーバ側は古いまま。

**案:** `SchedDataFile` に読み込み時の `mtime` を持たせ、`get_sdf()` で
食い違えば読み直す。上限も、TODO-069 で 1 リクエスト 63 日ぶんを読む
ようになった今の使い方に合わせて見直せる（20,000 は根拠が見えない）。

## D. `HandlerBase` が 3 つの役割を抱えている（TODO-081）

いま `handler.py` にあるのは、(1) `conf.json` の読み書き、
(2) 引数と設定値の変換・検証、(3) 表示に使える日付の範囲。
(2)(3) は `self` をログにしか使わない純粋な関数で、
`RequestHandler` を継承していることと関係が無い。
実際 `convert_value()` / `check_int_range()` は値を変換するだけの関数で、
`str2todo_days()` / `str2load_months()` は `MainHandler` 側にある。

**案:** (2)(3) をモジュールの関数として別ファイルへ出す。
テストがハンドラを組み立てずに書けるようになる。
ついでに、`MainHandler` しか使わない `CONF_KEY_LOAD_MONTHS` が
基底クラスにある、といった置き場所のズレも直せる。

## E. `main_handler.py` が 1,443 行（TODO-077・TODO-078）

`ytsched.py` 846 行に対して突出している。中身は 3 つに分かれる。

- ゲージの計算（`days2x_percent()` `calc_gauge_label()` `GAUGE`、約 90 行）
  — ハンドラと無関係な純粋な関数。**定数がファイル中に散らばっている**
  （`DAYS_GAUGE_K` は使う側の 2 つの関数より後ろに置かれている）
- 一覧の組み立て（`get()` `load_sched()` `load_todo()` ほか）
- 更新の実行（`post()` `exec_update()` `cmd_add()` `cmd_del()` ほか、約 400 行）

**案:** ゲージを別ファイルへ出すのは、依存が無いので今すぐできる（A と一緒に）。
更新側は `UpdateHandler` として分けるより、`exec_update()` 一式を
`SchedData` を受け取るクラスへ出すほうがきれいになる（B とも噛み合う）。

## F. `load_sched()` の引数 9 個（TODO-079）

TODO-021 で reviewer が挙げ、「挙動を変えない項目の範囲を超える」として
残された 1 件。TODO-069 で**週の数だけ繰り返し呼ぶ**ようになり、
9 個のうち 8 個は毎回同じ値を渡している。
さらに `mk_todo_by_date()` が呼び出しごとに `todo_sde` を全件走査するので、
前後 1 ヶ月（9 週）なら同じ集計を 9 回やっている。

**案:** 表示の条件（`filter_re` `filter_neg` `search_re` `search_mode`
`search_n` `todo_days_value` と ToDo の一覧）を 1 つの dataclass にまとめる。
呼び出しが `load_sched(monday, ctx)` になり、`todo_by_date` も
その中に 1 回だけ作れる。

## G. ハンドラへの依存の渡し方が `app.settings` 経由（TODO-081）

`SchedData` も画面の題名も `tornado.web.Application` の設定に入れ、
`HandlerBase.__init__` が `app.settings.get("sd")` で取り出している。
`self._sd` の型は `Any` になり、型チェッカが `SchedData` として見られない。

**案:** tornado の `initialize()` を使い、URL の登録時に
`(path, MainHandler, {"sd": self._sd})` の形で渡す。
型注釈が付き、`app.settings` を「文字列で引く入れ物」として使う場所が減る。

## H. `__init__.py` を読むと必ず tornado が読まれる（TODO-082）

`migrate.py` は「`handler.py` を import すると移行ツールが tornado に
依存してしまうので、設定ファイル名はここに持つ」とわざわざ書いてある。
ところが `__init__.py` が `MainHandler` と `WebServer` を import しており、
`__main__.py` も `from . import SchedDataFile, WebServer` なので、
`ytsched migrate` は結局 tornado を読み込む。**意図と実態が食い違っている。**

**案:** `__init__.py` が他のモジュールを import するのをやめる
（使う側がそれぞれのモジュールから直接 import する）か、
`migrate.py` のコメントを実情に合わせる。どちらでもよいが、
今の「片方だけ守っている」状態は、次に触る人を迷わせる。

## I. ブラウザ側（TODO-083）

- `my.js` 1,358 行がすべてトップレベルの `const`／`let`。
  中身は**スピナー / ゲージ / URL と遷移 / 週の管理 / キーボード /
  スワイプとマウス**の 6 つに、コメントできれいに分かれている。
  分かれているのだからファイルも分けられる（`base.html` の `<script>` を
  6 行にするだけ）。`elMain` `activeWeekOffset` のような状態が
  グローバルにあり、`main.html` の `<script>` から書き換えられている
  （`// declared in my.js` というコメントが付いている）のが、
  分けにくくしている一番の理由
- `main.html` の先頭に 120 行の `<script>` がある。テンプレートの値を
  使うのは `homeButtonHdr()` の `search_str` など数か所だけなので、
  値だけを `data-*` 属性か `<script>` の定数にして、関数本体は
  `my.js` 側へ移せる

## J. 使われていない属性を、テストが固定している（TODO-082）

- `HandlerBase._app` / `_req` — 代入されるだけで、どこからも読まれない
- `SchedDataFile.filename` / `dirname` — `src/` では未使用。
  `tests/test_ytsched.py:446-447` がアサートしているだけ
- `SchedData.get_keys()` — 呼び出しはすべてコメントアウトされたログ。
  `tests/test_ytsched.py:1043` がアサートしているだけ

テストがあるので「使われている」ように見えるのが厄介。消すなら
テストも一緒に消す判断が要る。

## K. 細かいもの（TODO-082）

- `__main__.py` の docstring が `"""main for musicbox package"""`（別のプロジェクトの写し）
- `cli` グループのヘルプが `sample package`、`x_data1` のヘルプが `test`。
  `x_data1` はデバッグ用と `src/README.md` に書いてあるが、
  `ytsched --help` には他の 2 つと並んで出る
- `webapp` の `--size_limit` の既定値だけ `100 * 1024 * 1024` を直書き
  （ヘルプの文字列は `WebServer.DEF_SIZE_LIMIT` を使っている）
- ruff の設定が `ignore` だけで `select` が無い（既定の `E4,E7,E9,F` のみ）。
  `--line-length 78` と `--extend-select I` は `mise.toml` の
  コマンド行にあり、`pyproject.toml` を見ても効いている規則が分からない
- `SchedDataFile.__init__` がパスを `str.split("/")` で分解している
  （`os.path` / `pathlib` を使っていない。`migrate.py` は `pathlib`）

---

## 手を付ける順（レビュー時点の見立て）

| | 中身 | 効き | 手間 | 項目 |
|---|---|---|---|---|
| 1 | **B**（`.bak` が中間状態）| データが戻せない | 中 | TODO-077 |
| 2 | **A + E の前半**（ゲージを分ける）| 食い違いの元を断つ | 小 | TODO-078 |
| 3 | **F**（`load_sched()` の引数）| 週ごとの重複計算も一緒に消える | 中 | TODO-079 |
| 4 | **C**（キャッシュが古くなる）| 手で直したデータが見えない | 小 | TODO-080 |
| 5 | **D・G・H・J・K** | 読みやすさ | 小 | TODO-081・TODO-082 |
| 6 | **I**（`my.js` の分割）| 触る前の見通し | 大 | TODO-083 |

着手する順番は利用者が決める。この表はレビューした時点での見立て。
