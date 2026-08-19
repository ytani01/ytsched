# TODO-005 reviewer の報告

`git diff`（未コミット、develop）を読んだ。起動確認・テスト実行はしていない。
コードは直していない。

**この報告は reviewer 自身が書けなかった（実行環境の制約で報告用の `.md` を
作れなかった）ため、返ってきた本文を main が転記した。**

## まとめ

- TODO-005 のチェックリストは **16 項目すべて、書いてあるとおりに直っている**。
  違う直し方をしたものは無い
- 実装そのものの誤り（境界条件・例外・既定値の評価）は**見つからなかった**
- ただし「`save()` が空でもファイルを書く」の副作用で、**`.bak` の中身が
  失われる経路が新しく増えている**（下記 1）。main の判断が要る
- 実装者が単独で決めた判断は 7 つとも妥当。**判断 1 は賛成**

---

## 確信度の高い指摘

### 1. `save()` が空でも書くようになり、`.bak` が空で上書きされる経路が増えた

`src/ytsched/ytsched.py:471`〜`484`（`SchedDataFile.save()`）

`save()` は毎回「既存ファイルを `.bak` へ move → 新しいファイルを書く」を
する。従来は `if self.sde:` があったため、**空の状態で `save()` を呼んでも
ファイルが作られず、次の `save()` は `os.path.exists()` が偽になって move を
しなかった**。今は空でもファイルができるので、次の `save()` が **0 バイトの
ファイルを `.bak` へ move してしまう**。

一時ディレクトリで実測した（`~/ytsched/data` は触っていない）。

**(a) 1 件しか予定が無い日の予定を編集した場合**（`cmd=fix` / `cmd=update`）。
`exec_update()` は `cmd_del()` → `cmd_add()` の順に呼び、それぞれが `save()`
するので 1 リクエストで `save()` が 2 回走る。

```
今回:   file='...新タイトル...'  bak=''                  ← 元の行が消えた
変更前: file='...新タイトル...'  bak='...元のタイトル...'
```

**(b) `cmd=del` を 2 回実行した場合**（削除後の URL をリロードする等）。
2 回目は消す対象が無いまま `save()` が走る。

```
今回:   1回目 bak='...元のタイトル...' → 2回目 bak=''
変更前: 1回目 bak='...元のタイトル...' → 2回目 bak='...元のタイトル...'
```

**現行データ（`.cgi` 本体）は正しいので、利用者に見える予定は失われない。**
失われるのは `.bak` だけ。補足として、**2 件以上ある日の編集では変更前から
すでに `.bak` が上書きされていた**（`cmd_del` の save で `.bak` が元の内容に
なり、続く `cmd_add` の save で「1 件消えた内容」に置き換わる）。1 件しか
ない日だけが偶然守られていた形で、今回それが他と揃ったとも言える。

判断が要るのは「`.bak` を直前の状態として当てにするか」。当てにするなら
`save()` の move 条件（空ファイルは退避しない、1 リクエストで 2 回保存しない
等）を別項目にするのが筋で、TODO-005 の範囲を超える。当てにしないなら
今のままでよい。

**この件以外に、`save()` を空でも書くようにしたことで壊れる箇所は
見つからなかった**（依頼 4 点目）。

- 0 バイトのファイルは `load()` が問題なく読める（`readlines()` が `[]`、
  `ok=True` のまま `out=[]`、`is_holiday` は `False`）。
  `test_save_empty_and_load` が押さえている
- `is_holiday` は `load()` 内でしか立たず、`main_handler.py:409` で渡すだけ。
  空ファイルなら `False` で正しい
- データファイルの存在を条件にしているコードは `save()` 内の
  `os.path.exists()` だけ（`glob` / `listdir` は無い）
- `save()` の呼び出し元は `SchedData.add_sde()` / `del_sde()` の 2 か所だけ
  なので、触っていない日に 0 バイトのファイルが増えることはない

---

## チェックリストの確認（依頼 1 点目）

16 項目を 1 つずつ実物で確かめた。すべて直っている。

| TODO の項目 | 実物 | 判定 |
| --- | --- | --- |
| `set_time()` を丸ごと削除 | 消滅（`grep` で残骸なし。`import time` も削除） | ○ |
| `get()` 先頭の死んだ `modified_sde_id` | 削除。後続の `= None` より前で参照する箇所は無い | ○ |
| `if sde.date == datetime.date(2021, 3, 1):` | 削除 | ○ |
| `print('DAYS_YEAR=...')` | 削除 | ○ |
| `save()` が空でも書く | `if self.sde:` 撤去。ただし上記 1 の副作用 | ○ |
| `load()` の 7 項目前提 | `len(d) < 7` で空文字埋め＋`d[:7]`。TODO の式と等価 | ○ |
| `load()` の `-` 前提 | `len(time1) < 2` で `['', '']`。指示どおり | ○ |
| `encoding=` 3 か所 | すべて指定。`LC_ALL=C` の回帰テスト 2 本追加 | ○ |
| `maxsplit=2` → `maxsplit=1` | 直っている。`test_load_conf_value_with_tab` あり | ○ |
| タブの無い行・空行 | `rstrip('\n')` → 空行は `continue`、タブ無しは warning で読み飛ばし | ○ |
| `new_id()` を uuid4 に | ID は `get_sde()` の一致比較にしか使われず、ソート・表示に使われていないことを確認 | ○ |
| `search_str` を先頭 1 か所に | 後半を削除し、先頭を後半のやり方に置換。指示どおり | ○ |
| `date` 既定値 | `date=None` にして `__init__` 内で今日に | ○ |
| `super().__init__()` を先頭へ | `handler.py:30` | ○ |
| `except Exception as ex: raise ex` | 削除 | ○ |
| キャッシュミスの warning | `debug` に | ○ |
| `autoreload=self._dbg` | 指示どおり。`debug=True` のときは tornado の `setdefault` で従来どおり効く | ○ |
| `r'&nbsp:'` → `r'&nbsp;'` | 直っている（キー重複も無し） | ○ |

- `xfail` は 6 件すべて外れている（`grep -rn xfail tests/` が空）
- `test_set_time_is_dead_code` は削除済み
- `TODO.md` のチェックボックスは未チェックのまま（main の担当なので指摘ではない）

---

## 判断 1 への賛否（依頼 2 点目）

**賛成。TODO の式をそのまま書くとデータが壊れるので、この追加は必要。**

1. 壊れる筋道が実際にある。`readlines()` の行末 `\n` は最終項目に残る。
   7 項目そろった行なら最終項目は `detail` で、`mk_dataline()` が
   `text2htmlstr()` を通す際に `rstrip('\n')` するので消える（`ytsched.py:66`）。
   ところが**項目が足りない行では最終項目が `type` / `title` / `place` の
   いずれかになり、これらは `text2htmlstr()` を通らずそのまま
   `'\t'.join(...)` される**。結果、保存後のファイルに余分な改行が入り、
   次の `load()` で空行の `int('')` が `ValueError` になる。実装者の報告どおり
2. 「項目が足りないときだけ」に限ったことで、7 項目そろった行の挙動が
   変わらず、TODO-003 が現状固定として書いた 2 本
   （`sde.detail == 'a\nb\n'`、`sde2.detail == sde.detail + '\n'`）に
   手を入れずに済んでいる。範囲を広げない直し方として妥当
3. 追加された `test_load_short_line_is_not_lost` が、この分岐が消えると
   落ちるテストになっている

より単純な形として、ループ先頭で `l.rstrip('\n').split('\t')` にすれば
短い行と 7 項目の行の扱いが揃い、`detail` に `\n` が増えるくせも消える。
ただし上記 2 のテスト 2 本を書き換えることになり、チェックリストには無い
変更なので、**今回のやり方のままでよい**と思う（気になるなら別項目）。

### 判断 2〜7

- **判断 2（Conf.cgi は読み書きとも utf-8）**: 妥当。euc_jp フォールバックを
  足すと読めた符号化と書く符号化が食い違って形式が揺れる。既存 `Conf.cgi` が
  euc_jp だと `UnicodeDecodeError` が `__init__` から素通しで全リクエスト
  500 になるが、**変更前もロケール依存で同じく落ちていた**ので悪化ではない
- **判断 3（`ENCODE[0]`）**: 妥当
- **判断 4（タブ無し行は warning で読み飛ばし）**: 妥当。握り潰していない。
  従来は `ValueError` が `HandlerBase.__init__` を抜けて **`Conf.cgi` が一度
  壊れると全リクエストが 500 になり続ける**状態だったので改善
  （例: `search_str` に `%0A` を含めると従来はこの状態になり得た）
- **判断 5（`date=None` は今日）**: 妥当。`cmd_add()` は `date=None` を
  明示的に渡す経路があり（フォームの `date` が空）、従来は `mk_dataline()` の
  `self.date.strftime()` で落ちていた。実際に効く直し
- **判断 6（位置）**: 妥当。下記で別途検証
- **判断 7（`render()` を mock）**: 妥当。`edit.html` は `search_str` を
  出さないので本文からは確かめられない。`mock.patch.object` は記述子では
  ないので `self` が渡らず `call_args.args[0]` がテンプレート名になるのも
  正しい。なお `render()` を潰すと tornado が空の 200 を返すので
  `post_body()` の 200 チェックは中身を見ていないが、テストの意図には合う

---

## `search_str` の統合の検証（依頼 3 点目）

**後続の挙動は変わっていない。**

- **`cmd=add` / `fix` / `del`**: 変更前は前半・後半の両方が走り、
  **最終的に使われるのは後半の値**だった。今回はその後半のやり方を先頭に
  置いただけなので値は同じ。前半が先に `set_conf()` して後半の `search_str0`
  が更新済みになるケースも追ったが、「引数と一致 → `pass`」に落ちるだけで
  最終値は変わらない
- **`set_conf()` が `exec_update()` の前になった**点は、`exec_update()` が
  設定を読み書きしないので影響なし（`Conf.cgi` へ入るのは小文字化前の
  生の値。これも後半ブロックと同じ）
- **検索モードの日付範囲**（`main_handler.py:319`〜）、`search_n`、ToDo の
  絞り込み、`sched` の組み立ては `search_str` の値だけを見ており、値が
  同じなので変わらない
- **`cmd=update`** は指示どおり挙動が変わる。テスト 2 本が押さえている
- 前半と後半の間で `search_str` を読む箇所は `cmd=update` の `render()` だけ
  であることを確認した

## `HandlerBase.__init__` の `super()` 移動（依頼 6 点目）

**問題なし。** `RequestHandler.__init__` は最後に `initialize(**kwargs)` を
呼ぶが、`HandlerBase` / `MainHandler` / `EditHandler` のいずれも
`initialize()` を定義しておらず、tornado 既定の no-op が呼ばれるだけ。
tornado が触る属性（`application` / `request` / `ui` / `_headers` 等）と
`HandlerBase` の `_dbg` / `_mylog` / `_app` / `_req` / `_conf` は衝突しない。
順序としてもこちらが正しい。

## テストの書き換え（依頼 5 点目）

**緩めて通しているものは見つからなかった。**

- `test_save_empty_writes_empty_file`: 中身が空であること、`.bak` が元の
  1 行であることまで見ている。変更前より強い
- `test_load_short_line_is_not_lost`: 判断 1 の分岐を実際に守っている
- ロケール依存のテスト 2 本: 終了コードだけでなく書かれたファイルの中身も
  utf-8 で読み直している
- `('a&NBSP;b', 'a b')`: 小文字の `&nbsp;` は変換表より前の `replace()` で
  消えるので、**直した行を実際に通るのは大文字だけ**。ケースの選び方は正しい
- `test_autoreload_is_not_forced`: assert は変更前と同じ（`xfail` を
  外しただけ）

---

## 確信度の低いもの（気になる程度）

**誤りだと確信しているわけではない。**

1. **`test_autoreload_with_debug` は pytest のプロセス内で
   `tornado.autoreload.start()` を実際に起動する**（`tests/test_webapp.py:60`）。
   tornado の `Application.__init__` が
   `if self.settings.get("autoreload"): autoreload.start()` を実行する
   （venv の `tornado/web.py` で確認）。`start()` は `IOLoop.current()` に
   500ms の `PeriodicCallback` を登録するので、(a) 閉じられない IOLoop が
   残る、(b) 万一その IOLoop が動く状況で監視対象の mtime が変わると
   `os.execv` で**テストプロセスごと再起動**しうる。実際に起きる確率は低い
2. **`load()` はデータファイルに空行があると今も `ValueError`**（`d[1]` が
   空で `int('')`）。`save()` が空行を書くことはないので実データでは
   起きにくく、チェックリストにも無い（実装者も気づいて残している）。
   今回 `load()` を「壊れた行でも読む」方向に直したので、揃えるなら別項目
   かもしれない
3. **時刻欄が `09-10` のように `:` を含まないと `IndexError`**
   （`time_start1[1]`）。TODO にあるのは `time1[1]` だけなので範囲外。
   2 と同じ扱い
4. **`edit.html:301` の `sde_id` 入力欄が `size="15"`。** uuid は 36 文字
   なので見切れる。`readonly` の表示だけなので実害は無いが、uuid 化の
   見た目の副作用
5. `load()` の `d[-1].rstrip('\n')` は `htmlstr2text()` のあとにかかるので、
   項目が足りない行の最終項目が `<br>` で終わっていると変換後の改行まで
   落ちる。保存時も `text2htmlstr()` が `rstrip('\n')` するので実害は無いはず
