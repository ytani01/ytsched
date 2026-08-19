# TODO-003 reviewer の報告

（reviewer が報告ファイルを書けなかったため、返答の内容を main が保存した。
本文は reviewer が書いたもの。）

## 前提の確認

`git status` のとおり変更は `pyproject.toml`（dev 依存 + コメントアウトした
`[tool.pytest.ini_options]`）だけで、`src/ytsched/` は 1 行も変わっていない。
TODO-003 の範囲を超えていない。`tests/__pycache__/` は `.gitignore` 済み。

全体としては良い出来。テスト側に `try` / `except` は 1 つも無く、期待値も
ほぼ全て直値（`days2y_offset(7) == 62`、`get_sortkey()` の文字列、タブ区切りの
データ行）。タブ区切りの往復も `test_mk_dataline` / `test_load` /
`test_web.py::test_add` がファイル上の literal と突き合わせているので、
片側だけの自己整合にはなっていない。xfail は 146 件中 6 件で付けすぎでもない。

---

## 確信度の高い指摘

### 1. `test_set_time_none` が、バグ由来の死んだ属性を xfail 無しで固定している

`tests/test_ytsched.py:264-267`

```python
def test_set_time_none():
    sde = mk_sde()
    sde.set_time(None, None)
    assert sde.time == SchedDataEnt.TIME_NULL
```

`grep` で確認したところ、`SchedDataEnt.set_time()` は `src/` のどこからも
呼ばれておらず、`set_time()` が設定する `self.time` も読まれる箇所が無い。
`set_time()` は丸ごと死んだコードで、`'02d' % t1[0]`（TODO-005）が今まで
気づかれなかったのはそのため。

TODO-005 で `'%02d'` に書き足すだけなら両テストとも整合するが、
**`time_start` / `time_end` を設定する形に作り替える／`set_time()` ごと消す**
という判断も十分ありうる（`self.time` は誰も使わないので `'%02d'` に直しても
何も改善しない）。その場合:

- `test_set_time`（270-275 行）は xfail(strict) なので、`sde.time` が
  `AttributeError` になっても「狙いどおり失敗した」ことになり
  **黙って通り続ける**。TODO-005 が済んだことをテストが教えない
- `test_set_time_none` は xfail が無いので**素直に落ちる**

依頼の主眼である「直すのをやめる方向に引っ張る」テストは、ここが唯一の
該当箇所。implementer は判断 6 で `test_set_time` の書き直しに触れているが、
`test_set_time_none` には触れていない。

### 2. `test_filter_str` / `test_search_str` の肯定側の assert が空振りする

`tests/test_web.py:106-113` と `:136-143`

```python
body = self.get_body(URL_PREFIX + '/', date=DATE1_STR, filter_str='歯医者')
assert '歯医者' in body
assert '定例ミーティング' not in body
```

`main.html` は `filter_str` / `search_str` を入力欄にそのまま出す
（`src/ytsched/webroot/templates/main.html:443-445` の
`value="{{ filter_str }}"`、同 370-373 行の `value="{{ search_str }}"`）。
`base.html` が `{% autoescape None %}` なので渡した文字列がそのまま本文に
現れ、この 2 つのフォームは条件節の外にあり常に描画される。

したがって `assert '歯医者' in body` は絞り込みの結果に関係なく必ず真になる。
**「filter_str を指定すると全件が消える」という壊れ方をしても、この 2 つの
テストは通る**（`'定例ミーティング' not in body` も満たされるため）。

同じ罠は `test_filter_str_negative`（115-127 行）の docstring では意識されて
いて、そちらは検索語（`病院`）と確認する語を分けてある。
`test_saved_filter_str_is_reused`（157-166 行）も同様で、こちらは有効。
この 2 つと同じやり方に揃えれば直る。`test_todo_with_filter_str` /
`test_todo_with_search_str` / `test_search_n_limits_days` は空振りしていない。

### 3. `detail` の往復が `rstrip('\n')` で覆われている

`tests/test_ytsched.py:346` と `:413`

```python
assert sde.detail.rstrip('\n') == 'a\nb'
assert sde2.detail.rstrip('\n') == sde.detail
```

implementer の「気づいたが直さずに残したもの 5」（保存→読み直しで `detail`
末尾に `\n` が増える）を `rstrip('\n')` で吸収している。`mk_dataline()`
どうしの比較でファイル形式の往復は担保されているので実害は無いが、この行だけ
読むと「`detail` は往復で一致する」と読めてしまう。直値（`== 'a\nb\n'`）に
するか docstring に現状として明記した方がよい。優先度は低い。

### 4. `test_new_id_is_unique` はタイミング依存で将来落ちうる

`tests/test_ytsched.py:101-103`

`new_id()` は `str(time.time()).replace('.', '-')` なので、連続 2 回が同じ
float を返すと重複する（現在のエポックでの float 分解能は約 1.2e-7 秒）。
今は `new_id()` 内の `cls._mylog.debug()` が時間を稼いでいるため通るが、
**TODO-007 でロガーを差し替えて速くなると落ちうる**。テストの問題であると
同時に実装側の潜在バグ（ID 衝突）でもある。TODO-005 の一覧には無いので
直すなら別項目。

---

## 確信度が低い / 参考

### 5. `test_webapp.py` の `WebServer` 生成がイベントループを 1 つ残す

`tornado/web.py:2269-2272` で `settings['autoreload']` が真だと
`tornado.autoreload.start()` が呼ばれ、`IOLoop.current()`
（`tornado/ioloop.py`）が実行中のループの無い状態では
`asyncio.new_event_loop()` + `set_event_loop()` でループをスレッドに設定した
ままにする。`webapp.py` は `autoreload=True` 固定なので `test_webapp.py` の
`svr` fixture などが毎回踏む。IOLoop を回さないので監視コールバックは発火せず
今は実害無し。TODO-005 で `autoreload=True` を外せば消えるので、テスト側の
対処は不要と思う。

### 6. `helpers.make_app()` が `webapp.py` の設定を写している

`tests/helpers.py:32-56` は `webapp.py:88-114` の手写し。`webapp.py` 側を
変えても `test_web.py` は追随しない。`test_webapp.py` が本物の設定を見ている
ので穴は塞がっているが二重管理ではある。`AsyncHTTPTestCase` の制約を考えると
現実的な妥協点。

### 7. `test_htmlstr2text` が変換表の書き損じを固定している

`tests/test_ytsched.py:49` の `('a&amp;nbsp:b', 'a b')`。元の変換表
（`ytsched.py:36`）の `r'&amp;nbsp:'` はセミコロンでなくコロンで、
`&amp;nbsp;` の書き損じに見える（`&amp;nbsp;` 自体は 44 行の `replace()` で
別途処理）。実害はほぼ無い。TODO-005 の一覧にも無い。

### 8. `test_load_hour_and_minute_are_normalized` について

`25:05` → `01:05` の丸めを固定している。壊れたデータを黙って別の時刻に
読み替える挙動だが、`load()` の意図的な防御に見え、TODO-005 の一覧にも無いので
現状固定で妥当。

### 9. `test_load_conf_line_without_tab` が 2 種類の行を同時に見ている

`tests/test_handler.py:82-90`。データは `'ToDo_Days\t365\n\nbroken\n'` で、
**空行**（`if line:` は `'\n'` を真と判定するので `split('\t')` が 1 要素に
なり `ValueError`）と**タブの無い行**の両方が入っている。今は先に空行で落ちる
ので docstring（「タブの無い行があっても」）とややずれる。TODO-005 では両方の
対処が要ると読める形にしておくとよい。

---

## implementer の「単独で決めた判断」について

- **判断 6**（`test_set_time` の期待値を `'09:05-10:30'`）— 期待値自体は
  `'%02d'` に直した場合の結果として正しい。ただし上の 1 のとおり
  **`test_set_time_none` の扱いが抜けている**。
- **判断 7**（既定値はシグネチャの型を assert）— 妥当。「読み込んだ日が今日で
  ある限り通ってしまうので strict xfail にできない」という判断は正しく、
  `inspect.signature(...).default` を見る形は `None` 番兵でも他の形でも通るので
  直し方を縛らない。
- **判断 10**（`save()` で空だとファイルが消える挙動を固定）— 現状固定で妥当と
  考える。`.bak` に退避された上で消えるので中身は失われず、「最後の 1 件を
  消したらファイルごと無くなる」は意図的な作りに見える。ただし
  `test_save_empty_removes_file` の docstring が「これが正しい」と読めるので、
  implementer の但し書き（仕様として違うなら別項目）をテスト側にも書いておくと
  よい。

## main の判断が要る点

1. 指摘 1 — TODO-005 で `set_time()` をどう直すか（`'%02d'` に直すだけか、
   作り替える／消すか）を先に決めておくと、テストの手直しが 1 回で済む。
2. 指摘 2 — TODO-003 の範囲内で直すか、TODO-005 以降に回すか。
