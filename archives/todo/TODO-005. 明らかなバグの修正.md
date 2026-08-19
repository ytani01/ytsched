# TODO-005. 明らかなバグの修正

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer
実施: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

分担の理由と各担当の報告は
[`archives/agents/TODO-005/`](../agents/TODO-005/README.md) にある。

## きっかけ

TODO-003（pytest によるテスト整備）で、動かしながらテストを書いていく中で
明らかなバグが 17 件見つかった。テストの側は現状の挙動を固定し、あるべき
挙動を `xfail(strict=True)` で 6 件だけ残してあった。

直し方に選択肢があるものは、着手する前に項目の中で決めておいた。
着手時に迷わずに済み、実装を分担に出せた。

## やったこと

### 直した 17 件（+ 作業中に見つかった 1 件）

**削除するだけのもの**

- `SchedDataEnt.set_time()` を丸ごと削除（`import time` も）。
  `'02d' % t1[0]` は `%` 抜けで必ず TypeError だが、どこからも呼ばれず、
  設定する `self.time` も読まれない死にコードだった
- `MainHandler.get()` 先頭の死んだ `modified_sde_id = ...`
- `main_handler.py` の `if sde.date == datetime.date(2021, 3, 1):`（残骸）
- `main_handler.py` の `print('DAYS_YEAR=...')`（import 時に出ていた）

**データが失われるもの**

- `SchedDataFile.save()` が `if self.sde:` のせいでデータファイルを消して
  いた（ある日の予定を全部削除すると、その日のファイル自体が無くなる）。
  **空でもファイルを書く**ようにした
- `SchedDataFile.load()` が 1 行 7 項目であることと、時刻欄に `-` が
  あることを前提にしていた。**足りない項目を空文字で埋めて読む**ように
  し、時刻欄に `-` が無ければ開始・終了とも空として扱うようにした
- **上の直しの副作用**で、`save()` が 0 バイトのファイルを `.bak` へ
  退避するようになっていた（下記）

**例外で落ちるもの**

- `save()` / `save_conf()` / `load_conf()` に `encoding=` が無く、
  ロケール依存だった（`LANG=C` で日本語の保存が落ちる）
- `load_conf()` の `split('\t', maxsplit=2)` — 値にタブが含まれると
  `ValueError`。`maxsplit=1` に直した
- `load_conf()` がタブの無い行・空行で `ValueError`。空行は読み飛ばし、
  タブの無い行は warning を出して読み飛ばすようにした

**挙動の直し**

- `SchedDataEnt.new_id()` を `str(uuid.uuid4())` に（`str(time.time())`
  では連続 2 回が同じ値になりうる）
- `MainHandler.get()` の `search_str` の処理が 2 か所にあり、
  `cmd=update` 経由だけ検索のクリアが効かなかった。`get()` の先頭
  1 か所にまとめ、後半のやり方（空文字も保存する、`.lower()` する）に揃えた
- `SchedDataEnt.__init__` の既定値 `date=datetime.date.today()`
  （import 時に 1 回だけ評価されていた）を `None` にし、`__init__` の中で
  今日の日付にした
- `HandlerBase.__init__` の `super().__init__()` を先頭へ
- `webapp.py` の `except Exception as ex: raise ex` を削除
- 正常系のキャッシュミスの `warning` を `debug` に
- `autoreload=True` の固定を `autoreload=self._dbg` に
- `htmlstr2text()` の変換表の `r'&nbsp:'` を `r'&nbsp;'` に

### 作業中に見つけて、同じ項目の中で直した 1 件

「`save()` が空でもファイルを書く」の副作用で、**0 バイトのファイルが
`.bak` へ move されるようになっていた**。reviewer が見つけ、main が実測で
確かめた。

```
add後      file='id-1 … 大事な予定'   bak=なし
del 1回目  file=''                     bak='id-1 … 大事な予定'
del 2回目  file=''                     bak=''      ← データが完全に消えた
```

最後の 1 件を消した直後はデータが `.bak` にしか無いので、同じ `cmd=del` が
もう一度走ると（削除後の画面をリロードすると POST が再送される）両方とも
空になる。変更前は 2 回目の `os.path.exists()` が偽になって `.bak` が
守られていた。**この項目の直しが作った経路なので、同じ項目の中で塞いだ。**

`save()` の move を「既存ファイルが存在し、かつ 0 バイトでないとき」に
限定した。判定を `self.sde` の中身ではなくディスク上のファイルサイズで
行っているのは、`.bak` を空で潰さないという趣旨に直結し、読み込み後に
ファイルが外部で変わった場合にも効くため。

これで、1 件しか予定が無い日を `cmd=fix` / `cmd=update` で編集したときにも
`.bak` が守られる（`exec_update()` は `cmd_del()` → `cmd_add()` を呼ぶので、
1 リクエストで `save()` が 2 回走り、2 回目が 0 バイトのファイルを移していた）。

### TODO.md に書いた直し方から変えた 1 か所

`load()` の項目埋めは、TODO.md では `d = (d + [''] * 7)[:7]` と書いて
いたが、**そのままではデータが壊れる**ことが実装中に分かった。

`readlines()` の行末 `\n` は最終項目に残る。7 項目そろった行なら最終項目は
`detail` で、`mk_dataline()` が `text2htmlstr()` を通す際に `rstrip('\n')`
するので消える。ところが**項目が足りない行では最終項目が `type` /
`title` / `place` のいずれかになり、これらは `text2htmlstr()` を通らず
そのまま `'\t'.join(...)` される**。結果、保存後のファイルに余分な改行が
入り、次の `load()` で空行の `int('')` が `ValueError` になる。

**項目が足りないときだけ**最終項目の `\n` を落としてから埋めるようにした。
7 項目そろった行の挙動（`detail` 末尾に `\n` が残る）は従来どおりなので、
TODO-003 が現状固定として書いたテストに手を入れずに済んでいる。

reviewer もこのやり方に賛成した。より単純な形として、ループ先頭で
`l.rstrip('\n').split('\t')` にすれば短い行と 7 項目の行の扱いが揃い、
`detail` に `\n` が増えるくせも消えるが、テスト 2 本の書き換えを伴い
チェックリストにも無いので、今回はやっていない。

## テスト

`uv run pytest -q` — **161 passed**（作業前は 140 passed, 6 xfailed）。
`LANG=C uv run pytest -q` でも 161 passed。**`xfail` は 0 件**。

- TODO-003 で付けた `xfail(strict=True)` 6 件をすべて外した
- `set_time()` の削除に伴い `test_set_time_is_dead_code` を削除した
- **バグのある挙動を固定していたテスト 3 本を、直した挙動に書き直した**
  （`test_save_empty_removes_file` →
  `test_save_empty_writes_empty_file`、`test_sched_data_del_sde`、
  `test_web.py::TestUpdate::test_del`）。TODO-005 は直し方を決めた項目
  なので、テストの側が古くなった形
- テストの無かった直しに 14 本足した。ロケール依存の確認は
  `helpers.run_in_c_locale()`（`LC_ALL=C` + `PYTHONUTF8=0` +
  `PYTHONCOERCECLOCALE=0`）を用意して、書かれたファイルの中身まで見ている

`verifier` がアプリを実際に起動して確かめた（`--datadir` は一時ディレクトリ）。

- 起動時に `DAYS_YEAR=...` が出ない。メイン画面は 200 でテンプレートも展開
- `cmd=del` で最後の 1 件を消してもデータファイルが 0 バイトで残り、`.bak` に
  元データが残る。**同じ `cmd=del` を 2 回送っても `.bak` は守られる**
- 1 件しかない日を `cmd=update` で編集しても `.bak` に編集前の内容が残る
- 壊れたデータファイル（項目 3 個の行、時刻欄に `-` の無い行）でも 500 に
  ならない。壊れた `Conf.cgi`（空行・タブ無し行・値にタブを含む行）でも
  200 で、ログは読み飛ばしの warning 1 行だけ
- サーバのログに例外・トレースバックは無し

## 残したもの

「やらないと決めたもの」として項目に書いてあったもの。

- `SchedData.get_sdf()` の破棄数 `int(cache_size * 0.1)` が `cache_size`
  10 未満で 0 件になる件 — 既定の 20000 では問題にならず、10 未満にする
  使い方も無いので直さない
- `SchedDataEnt.__init__` が `self.__class__._mylog` を上書きしている件 —
  ロガーの持ち方そのものの話なので TODO-007 へ回した

範囲外として残したもの（reviewer / implementer が挙げた）。

- **2 件以上ある日を `cmd=update` で編集すると、`.bak` が「編集前」では
  なく「対象を削除した中間状態」になる。** `save()` が 2 回走り、2 回目は
  本体が空でないので move されるため。**この挙動は変更前からあった**
  （1 件しかない日だけが偶然守られていた）。`.bak` を直前の状態として
  当てにするなら、`save()` の呼び方そのものを見直す別項目が要る
- `load()` はデータファイルに空行があると `int('')` で `ValueError`。
  時刻欄が `09` のように `:` を含まないと `time_start1[1]` で `IndexError`。
  今回 `load()` を「壊れた行でも読む」方向に直したので、揃えるなら別項目
- `test_autoreload_with_debug` は pytest のプロセス内で
  `tornado.autoreload.start()` を実際に起動する（`Application.__init__` が
  `autoreload` 設定を見て呼ぶ）。閉じられない IOLoop が残る
- `edit.html` の `sde_id` 入力欄が `size="15"` で、36 文字の uuid が
  見切れる（`readonly` の表示だけなので実害は無い）
- 行長 78 超え（`main_handler.py`）は TODO-004、型ヒントは TODO-006、
  ロガーは TODO-007、正規表現入力の扱いは TODO-012

## この項目で分かった、進め方の話

**サブエージェントが報告ファイルを書けなかった。** Claude Code 本体
（v2.1.235）に `^(REPORT|SUMMARY|FINDINGS|ANALYSIS).*\.md$`（大文字小文字を
無視）を弾くガードがあり、TODO-013 で決めた `report-<担当名>.md` という
名前がちょうど一致していた。今回は 3 通とも main が転記した。
名前を変える話は **TODO-014** として別に立てる。
