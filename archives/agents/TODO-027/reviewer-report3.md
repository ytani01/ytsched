# TODO-027 reviewer の報告（3 回目）

`git diff`（`src/ytsched/handler.py`・`main_handler.py`・`edit_handler.py`、
`tests/test_web.py`・`test_main_handler.py`、`TODO.md`）と、周辺の
`ytsched.py`（`add_sde()`/`del_sde()`/`SchedDataEnt.__init__`）・
`src/README.md` を読んだ。コードは直していない。作業ツリーを戻す
コマンドは使っていない（`git diff` / `git status` だけ）。

---

## 直っているもの

### 指摘 1（`month`/`day` の `OverflowError`）は直っている

`main_handler.py:270-277`。`year`/`month`/`day` の 3 つとも
`datetime.date()` を**呼ぶ前に** `check_int_range()` を通る。
`month=99999999999` / `day=±99999999999` は `ValueError` になり、
`convert_value()` の `except ValueError` で拾える。3 つが同じ形に
揃っていて読みやすい。

### 指摘 2（更新経路の `date`/`orig_date`）は、500 という意味では直っている

`main_handler.py:940-942`。`get_date_arg()` が
`convert_value(arg_name, value, self.str2date)` になり、`date` も
`orig_date` も、形式・範囲の両方を見るようになった。
`cmd=add&date=abc` / `date=9999-12-31` は 500 にならない。
**ただし「落ちたあとどうするか」に判断が要る（下の指摘 1・2）。**

### 指摘 3（`EditHandler` の `date`）は直っている

`edit_handler.py:63`。`/edit` は URL に日付を含む経路が無い
（`webapp.py` のルートは `{prefix}/edit` だけ）ので、`date` を塞げば
`EditHandler` に他の 500 の口は無い。

### 1・2 回目の実装は欠けていない（依頼書 6）

`git checkout -- src` の事故による欠落は見当たらない。2 回目の報告で
挙げたものは、`HandlerBase` への移動を差し引いて全部そのまま残って
いる。

| もの | 今の場所 |
|---|---|
| `convert_value()` | `handler.py:120` |
| `date_range()` | `handler.py:154` |
| `check_date()` | `handler.py:176` |
| `str2date()` | `handler.py:197` |
| `check_int_range()` | `handler.py:214`（新規） |
| `SEARCH_MODE_MAX_DAYS` | `handler.py:27` |
| `str2ymd_date()` / `ymd2date()` | `main_handler.py:249` / `516` |
| `str2todo_days()` | `main_handler.py:279` |
| `get_conf_arg()` の総称化と `convert=` | `main_handler.py:305` |
| `get_date()` の `cur_day` / `date` / `year+month+day` | `main_handler.py:481-509` |

### `get_date()` が返す日付は、どの経路でも範囲内

`cur_day` / `date` / `year+month+day` は `check_date()` を通る。
`modified_date` だけは `check_date()` を通らないが、その出どころは
`new_sde.date` で、`date` 引数が範囲外なら `None` → `SchedDataEnt` 側で
今日になるので、範囲外の日付が `load_sched()` へ届く経路は残っていない。
**`get_date()` 側にチェック漏れがあるように見えるが、穴にはなっていない。**

### 残っている 500 の経路（依頼書 1）

**`get_time_arg()` だけ。** 実装者の申告どおり。`main_handler.py:961` の
`datetime.time.fromisoformat(value)` が素通しで、`time_start=abc` /
`time_end=abc` は 500。`exec_update()` の中で `cmd_del()`/`cmd_add()` より
**前**に呼ばれるので、途中まで書いて落ちることは無い（データは壊れない）。

ほかは見当たらない。確かめたもの:

- `deadline_date` / `deadline_time_start` / `deadline_time_end` は
  文字列のまま `detail` に埋めるだけで、パースしない
- `sde_align` / `todo_flag` / `sde_type` / `title` / `place` / `detail` /
  `sde_id` / `cmd` はすべて文字列比較
- `search_str` / `filter_str` は `compile_re()` が例外を拾う（TODO-012）
- `search_n` に範囲が無いのは今までどおりだが、`search_count >= search_n`
  に使うだけなので、負値・巨大値でも落ちない
- `--days` を極端に大きくしたときの `date_range()` は指摘 6 のとおり
  範囲外。ただし `str2date()` が `EditHandler` からも呼ばれるように
  なったので、**影響する画面が `/edit` にも広がった**（`--days` は
  CLI の値なので、この項目でやることではない）

---

## 確信度の高い指摘

### 1. 更新経路の「読めない日付 ＝ 今日」は、既存データを別の日へ動かす

`main_handler.py:844-846`（`exec_update()` の `date`）、`940-942`

`cmd=update` / `fix` で `orig_date` は正しく、`date` だけが読めない
（または範囲外の）とき、こうなる。

| 入力 | 前（TODO-027 の前） | 今 |
|---|---|---|
| `cmd=update&orig_date=2021-03-01&date=9999-12-31&sde_id=…` | 500。**書き込みは 1 つも起きない** | `2021-03-01` から**消えて**、今日のファイルへ移る |

`get_date_arg()` は `cmd_del()` より前に呼ばれるので、以前はここで
落ちてデータが変わらなかった。今は「日付が読めない ＝ 今日のことだ」と
解釈して、**既存の 1 件を今日へ移す**。

表示経路（`date`/`cur_day`/`year+month+day`）で「無視して既定値」に
するのは、画面が出るだけで実害が無いから妥当だが、**書き込む経路で
同じ扱いをすると、利用者が指定していない日へデータが動く**。
`date` が空の POST を今日にする TODO-016 の決めごとは「空 ＝ 省略」の
話で、「読めない値」を同じ扱いにしてよいかは別の判断。

**どうなると困るか。** 手で組んだ URL、壊れたリンク、古いブックマーク
から `cmd=update` が飛んだとき。編集フォーム（`<input type="date">`）
からは起きない。

### 2. `orig_date` が読めないときの扱い — `del` は妥当、`fix`/`update` は考え直したほうがよい（依頼書 2）

`main_handler.py:832-841`、`894-901`

**`cmd=del` は現状で妥当。** 「どのファイルか分からないから消さない」は
正しい。`None` に落として `ToDo.jsonl` を消しに行くよりずっとよく、
理由も報告に書かれている。

**`cmd=fix`/`update` の「消さずに足す」は、賛成できない。**

- 同じ `sde_id` の予定が 2 件できる。**コードは「1 つのファイルの中で
  `sde_id` は一意」を前提にしている**。`SchedDataFile.del_sde()`
  （`ytsched.py:608-618`）は最初に見つけた 1 件を消して `break`、
  `get_sde()` も最初の 1 件を返す
- 新しい `date` がたまたま元の予定と同じ日だと、**同じファイルに同じ
  `sde_id` が 2 行**並ぶ。この状態で画面から片方を消すと、消えるのは
  「並び順で先に来たほう」で、利用者が消したつもりのものとは限らない。
  つまり、`del` で防いだはずの「消し間違い」を、`fix`/`update` の側で
  作っている
- 「消えたデータは戻らないが重複は消せる」という理由は分かる。ただ
  `fix`/`update` は「この 1 件を置き換える」という操作なので、**半分
  だけ実行する**のは、実行しないより分かりにくい

**私の見立て（推す順）。**

1. **更新系（`fix`/`update`/`del`）で `orig_date` が渡されているのに
   読めないときは、`tornado.web.HTTPError(400)` を返す。**
   前例がある（TODO-016 で「存在しない `sde_id` は 404」）。
   400 は 500 ではないので、この項目の目的（不正な入力で 500 に
   しない）は満たす。UI からは絶対に起きない入力なので、普通の操作は
   何も変わらない。**指摘 1 の `date` も同じ扱いにできる**ので、
   「書き込む経路は、読めない引数を受け取ったら断る」で一本に揃う
2. **コマンドごと何もしない**（消しも足しもしない）。データが変わらず、
   重複も作らない。ただし、利用者から見ると「押したのに何も起きない」
   になる
3. 今の実装（消さずに足す）

**決めるのは main。** 1 を採るなら `TestInvalidUpdateArgs` の
`test_update_with_unreadable_orig_date_keeps_the_original` と
`test_add_with_*` は書き直しになる。

### 3. `src/README.md` の `HandlerBase` の説明が実物とずれた

`src/README.md:14`, `55-58`

どちらも `HandlerBase` を「`Conf.cgi` の読み書き」とだけ書いている。
今は `convert_value()` / `date_range()` / `check_date()` / `str2date()` /
`check_int_range()` / `SEARCH_MODE_MAX_DAYS` が入って、**引数の変換と
検証の置き場所**でもある。

`src/README.md` は `CLAUDE.md` が「コードを触る前に必ず開くこと」と
名指ししている文書なので、ここがずれていると、次に触る人は変換まわりを
`MainHandler` に探しに行く。**この項目の中で 1〜2 行足すのが良い**
（`.md` はもう archives の分がコミットに入るので、`wording` は
どのみち要る）。

---

## 確信度の低いもの・細かいもの

### 4. `orig_date_is_broken` の二度読みは、動くが遠回り

`main_handler.py:838-841`

`get_argument("orig_date")` を読んでから `get_date_arg("orig_date")` を
呼び、その中でもう一度同じ引数を読んでいる。Tornado の
`get_argument()` は同じ値を返す（`strip=True` も両方に効く）ので
**バグにはならない**。ただ「戻り値が `None` になった理由を、引数を
読み直して当てる」形なので、素直にするなら `exec_update()` の中で
直接書くほうが短い。

```python
orig_date_str = self.get_argument("orig_date", None)
orig_date = None
if orig_date_str:
    orig_date = self.convert_value(
        "orig_date", orig_date_str, self.str2date
    )
orig_date_is_broken = bool(orig_date_str) and orig_date is None
```

指摘 2 で 400 を選ぶなら、この変数自体が消える。**優先度は低い。**

### 5. `SEARCH_MODE_MAX_DAYS` を `HandlerBase` に置いたのは、受け入れてよい（依頼書 3）

数字を 2 か所に書くよりはよく、コメントも付いている。ずれているのは
**名前と場所の対応**だけ。`EditHandler` は検索をしないのに、
「検索モードで遡る最大の日数」で使える日付の範囲が決まる。
役割で名前を付け直す（`date_range()` が使う余白として別名にして、
`MainHandler` 側がそれを参照する）手もあるが、**この項目でやることでは
ない**と思う。

`check_int_range()` が `HandlerBase` にあるのは自然。`check_date()` と
同じ「`datetime` へ渡す前に弾く」役目で、`str2date()` の隣に並んでいる。
使い手が今 `MainHandler` だけなのは気にしなくてよい。

### 6. `day` を 1..31 で先に弾くのは、日付の正しさの判断を変えていない（依頼書 4）

**受け入れる日付の集合は前と同じ。** `day=0`/`day=32` は前も
`datetime.date()` が `ValueError` にしていたし、月末（2 月 31 日など）は
今も `datetime.date()` が見ている。変わるのは警告文だけで、
`day must be in 1..31, not 32` のほうが `year`/`month` と揃っていて
読みやすい。**問題無し。**

### 7. 足したテスト 13 件は挙動を固定している（依頼書 5）

- `test_del_with_unreadable_orig_date_keeps_todo` が本丸。`None` へ
  落として `ToDo.jsonl` を消してしまう実装を確実に落とす
- `test_del_with_unreadable_orig_date_deletes_nothing` が、`date` へ
  フォールバックして別のファイルを消す実装を落とす
- `test_update_with_unreadable_orig_date_keeps_the_original` は、
  「元の 1 件が残る」と同時に**重複ができること**も固定している。
  指摘 2 の判断次第で書き換えになる（悪いテストという意味ではなく、
  今の判断をそのまま写しているということ）
- 足すとしたら、**`orig_date` が正しいときに削除が効く**ことを同じ
  クラスに 1 件。ガードが全部の削除を止めていないことが、その場で
  読める。既存の `TestUpdate` にあるので必須ではない

### 8. ログの出どころが `handler.py` に変わる

`convert_value()` が `HandlerBase` に移ったので、警告の
`{file}:{line} {function}()` が `handler.py:…convert_value()` になり、
`mylog` の名前別の水準も `"HandlerBase"` 側になる（`_MainHandler__log`
ではなく `_HandlerBase__log` を使うため）。今は名前別の水準を設定して
いる場所が無いので**実害は無い**。

### 9. `cmd=del` に「正しいが予定の無い日」を渡すと、今も空ファイルができる

`ytsched.py:794-816` の `del_sde()` は、見つからなくても `sdf.save()` を
呼ぶので、`{year}/{month}/{date}.jsonl` が空で作られる。**この diff で
できた話ではない**（TODO-005 の頃からの挙動）。むしろ今回、範囲外の
`orig_date` が `cmd_del()` に届かなくなったぶん減っている。記録だけ。

---

## main の判断が要るところ

1. **指摘 1・2** — 更新経路（`cmd=add`/`fix`/`update`/`del`）で日付が
   読めないときに、**今日へ寄せる／何もしない／400 を返す**のどれに
   するか。私は 400 を推す。1 と 2 は同じ判断で片付く
2. **指摘 3** — `src/README.md` の `HandlerBase` の説明を、この項目で
   直すか
3. **`get_time_arg()`**（`time_start=abc` で 500）を、この項目に足すか
   別項目にするか。`convert_value(arg_name, value, datetime.time.fromisoformat)`
   に載せるだけで塞がるが、「読めない時刻を `None`（時刻無し）にして
   よいか」は指摘 1 と同じ判断になる
