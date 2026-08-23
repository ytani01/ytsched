# TODO-028 reviewer の報告

見たもの: `git diff` の 4 ファイル
（`src/ytsched/main_handler.py`、`src/ytsched/ytsched.py`、
`tests/test_main_handler.py`、`tests/test_ytsched.py`）。
`TODO.md` の「TODO-028」、`archives/agents/TODO-028/implementer-request.md`、
`implementer-report.md` を先に読んだ。
起動確認・テスト実行はしていない（verifier の担当）。

## 総評

**正しさの点で、直すべき欠陥は見つからなかった。** 5 件とも項目の範囲内で、
範囲を超えた変更も無い。実装報告の「単独で決めたこと」6 点は、下記のとおり
1・2・3・5・6 は妥当、4 だけ設計上の意見がある。

以下、確信度の高い順に書く。

---

## 1. 実装の判断（依頼にあった重点）

### 1-1. `continue` ではなく「開かずに空として扱う」（妥当）

**この判断は正しい。** `load_sched()` の `sched.append(...)` は検索モード
以外では毎日必ず走るので、日ごと `continue` すると通常表示でその日の欄が
消える。実装報告の説明のとおりで、コードを追っても確認できた。
`sdf = None` 経路で `sched` に入る値が変わらないことも確かめた。

- `is_holiday`: `SchedDataFile.is_holiday` は `load()` の中で
  **ファイルの中身からだけ**決まる（`ytsched.py:448-472`）。曜日や祝日
  ファイルは見ていないので、ファイルが無い日は必ず `False`。
  `sdf.is_holiday if sdf else False` は元と同じ値になる
- `search_count`: 加算はファイル側の `sde` ループの中だけなので、
  空として扱っても数え方は変わらない
- `SchedDataFile` は `__bool__`/`__len__` を持たないので、`if sdf` は
  「`None` かどうか」と一致する（`ytsched.py` に dunder は
  `__init__`/`__str__` だけ）

### 1-2. `mk_todo_by_date()` の追加（妥当。結果は変わらない）

- 旧: 日ごとに `todo_sde` 全件へ `search_match()` → `sde.date == date1`
- 新: 先に `search_match()` を通したものを `sde.date` で束ねて引く

`out_sde` に入る要素と順序は一致する（同じ日の中の順序は `todo_sde` の
まま、最後の `sorted()` は安定ソートなので同着の並びも変わらない）。
`todo_days_value < 0` のときに空 `dict` を返すのも、呼び出し側の
`if todo_days_value >= 0:` と揃っている。`sde.date` が `None` の ToDo が
あっても、`None` キーは `get(date1)` で引かれないので旧実装と同じ結果。

なお `load_todo()` が既に `search_match()` を通したものだけを `todo_sde`
に入れている（`main_handler.py:639`）ので、`mk_todo_by_date()` の
`search_match()` は元のコードと同じく二重の照合になっている。**挙動を
変えないためにはこれで正しい**（消すと挙動は変わらないはずだが、
この項目の範囲を超える）。

### 1-3. `date2path()` を classmethod に（妥当。ただし後述の 2-1）

呼び出し元は `SchedDataFile.__init__` の `self.date2path(...)` と、新しい
`SchedData.sdf_exists()` の 2 か所だけ。`self` を使っていなかったので
classmethod 化は自然で、既存の呼び出しもそのまま動く。

### 1-4. `get_conf_arg()` の保存方針（動作は正しい。設計は意見あり）

`isinstance(converted, str)` で「変換後」か「渡された文字列」かを選ぶ実装
そのものは、現在の 4 か所すべてで意図どおりに動く
（`filter_str`→小文字を保存、`search_n`/`todo_days`→`"007"` のまま保存、
`search_str`→`convert=str` なので実質そのまま）。副作用として
`filter_str=ABC` を送ったとき、`Conf.cgi` が既に `abc` なら書き込みが
起きなくなる（結果は同じで、書き込みが減るだけ）。

**意見（正しさの問題ではない）**: `get_conf_arg[T]` は型引数で一般化して
おきながら、保存の形を `T` の**実行時の型**で決めている。「文字列を返す
変換だけは変換後を保存する」という規則が引数からは読めず、docstring で
説明するしかなくなっている。`save_converted: bool` のような明示的な引数
か、呼び出し側で正規化してから渡す形のほうが意図が現れる。TODO-029 で
`search_str` も `normalize()` になると、結果的に「str を返すものは全部
変換後を保存」になるので、そのときに見直す手もある。**判断は main。**

### 1-5. `search_str` を揃えなかった判断（妥当）

依頼が `filter_str` の 2 件だけを挙げているので、範囲を守った判断として
正しい。`SearchStr` は元のまま・`FilterStr` は小文字、というちぐはぐな
状態が TODO-029 まで残るが、**それは TODO-029 の範囲**。

### 1-6. ゴールデンマスターテストの書き直し（妥当）

`tests/README.md` の「挙動を変える変更なら、そのテストも合わせて書き直して
よい」に沿っている。書き直した 4 本はいずれも、新しい挙動を正しく固定して
いる（`FilterStr\t\n` の行は `load_conf()` の `rstrip("\n")`＋タブ分割で
空文字として読み戻せることも確かめた）。

---

## 2. 指摘

### 2-1. `src/README.md:76-77` が実装と食い違うようになった（確信度: 高）

> 入力欄の文字列と `Conf.cgi` への保存は不正でもそのまま残し、

`filter_str` は**小文字にしてから**入力欄と `Conf.cgi` に入るように
なったので、「そのまま残し」は正しくなくなった（「不正な正規表現でも
捨てない」という主旨のほうは今も正しい）。

- 実際に見える差: `\D`（数字以外）と打つと、入力欄が `\d` になって
  返ってくる。**照合の結果は変わらない**（変更前も照合は `.lower()` 済み
  の文字列で行っていた）ので機能上の後退ではないが、**利用者が打った
  正規表現が書き換わって保存される**ようになったことは、この段落の説明と
  食い違う
- implementer は「TODO-029 でまとめて見直すのがよい」として直していない。
  文書と実装が食い違う期間ができることを承知のうえで先送りするか、この
  1 文だけ今直すかは **main の判断**

（`docs/data-format.md:147-179` の「判定・検索に使う正規化」は
`SchedDataEnt` 側と旧形式の話で、`Conf.cgi` には触れていない。同 30 行目に
「Conf.cgi は対象外」とあるので、implementer の「data-format.md は直さなくて
よい」という判断のほうは妥当。）

### 2-2. `date2path()` を単独で呼ぶと `~` が展開されない（確信度: 中／現状はバグではない）

`ytsched.py:403` の既定値は `topdir: str = DEF_TOP_DIR`＝`"~/ytsched/data"`
で、`date2path()` 自身は `expanduser()` しない。展開しているのは
`SchedDataFile.__init__`（`self.topdir` を作るとき）と、新しい
`SchedData.sdf_exists()`（呼ぶ直前）の**2 か所に分かれている**。

- 今の 2 つの呼び出しは両方とも展開済みの `topdir` を渡すので**現状は
  正しく動く**
- ただし docstring に「ファイルを開かずにパスだけ知りたいことがあるので、
  インスタンスを作らずに呼べるようにしてある」と書いて単独呼び出しを
  勧める形になったため、`SchedDataFile.date2path(date)` と `topdir` を
  省いて呼ぶ道が開いた。その戻り値は `~/ytsched/data/...` のままなので、
  `os.path.isfile()` は**例外も警告も出さずに常に `False`** を返す
  （「その日はデータが無い」と誤判定して黙って飛ばす）
- 展開する場所を 1 か所（`SchedData.__init__` で `_topdir` を展開する、
  または `date2path()` の中で展開する）に寄せれば、この道は塞がる。
  **直すかどうかは main の判断**（この項目の範囲を少し超える）

---

## 3. 気になった程度（確信度: 低）

いずれも「直すべき」とまでは言えないもの。

1. **`tests/test_main_handler.py`
   `test_saved_filter_str_is_not_rewritten_when_unchanged`** — 名前は
   「書き直されない」だが、assert は最終的な `Conf.cgi` の中身しか見て
   いないので、書き直しが起きたかどうかは確かめていない（書き直されても
   同じ内容になるため通る）。名前が assert より多くを主張している
2. **`assert skipped == opened`（同ファイル
   `assert_same_as_opening_every_day`）** — `SchedDataEnt` は `__eq__` を
   持たないので、この比較は同一オブジェクトかどうかで通っている。同じ
   `SchedData`（＝同じキャッシュ）を使い回していて、2 回目が
   キャッシュから同じオブジェクトを返すから一致する。今は正しく動くが、
   キャッシュの実装が変わると**挙動が正しくても落ちる**テストになっている
3. **`test_cookie_todo_days_is_removed`** — 定数が無いことを見るテスト。
   意図（同じものを足し直さないための覚え書き）は docstring に書いてあり
   分かるが、挙動を確かめるテストではない
4. **`for sde in sdf.sde if sdf else []:`** — `if sdf is not None` のほうが
   意図が直接読める（今は `SchedDataFile` に `__bool__`/`__len__` が無い
   ので同じ意味。仮に将来 `__len__` が付いても結果は変わらないことは
   確かめた）
5. **画面下部の `{{ sd.get_cache_size() }}`（`main.html:413`）に出る数字が
   大きく減る。** 意図した変化だが、目に見える表示なので念のため
6. `fix_todo_done()` で `deadline_date_str` が空のとき、`detail` の先頭が
   `〆 ` から `〆` に変わる（元から不自然な出力で、この変更で悪くは
   なっていない）

---

## 4. 確かめて問題が無かったこと

- `filter_str` の空送信で絞り込みが解除される経路: `main.html:456-466` の
  `form_filter` は `filter_str` と `cur_day` だけを送る。`doSubmit()`
  （`my.js:208`）は該当フォームを submit するだけなので、**日付送りや
  `todo_days` の変更で `filter_str=""` が紛れ込んで絞り込みが消える**
  ような経路は無い
- `〆` 行を読み直して解釈しているコードは無い（`grep` で確認）。区切りの
  空白を落としても、読み込み側に影響しない。旧形式のテストデータ
  （`tests/data/old_format/ToDo.cgi`）の `〆2026/09/16` にも空白は無く、
  むしろ元の形に戻っている
- `COOKIE_TODO_DAYS` の参照は、テンプレート・JS を含めて他に無い
- `date2path()` の既存の呼び出し・テストは classmethod 化の影響を受けない
- `sdf_exists()` がキャッシュを先に見るのは正しい（保存前の
  `SchedDataFile` を取りこぼさない）
- 変更はすべて TODO-028 の 5 件の範囲内。`sde_align`（TODO-024 で「今の
  ままでよい」と決めた件）には触れていない

---

## 5. main の判断が要る点

1. **`src/README.md:76-77` の「そのまま残し」を今直すか、TODO-029 まで
   置くか**（指摘 2-1）
2. **`expanduser()` の置き場所を 1 か所に寄せるか**（指摘 2-2。今は
   バグではないので、TODO-029 以降でもよい）
3. **`get_conf_arg()` の保存方針を実行時の型で決める形のままにするか**
   （1-4。TODO-029 で `search_str` も `normalize()` になるときが見直しの
   機会）
