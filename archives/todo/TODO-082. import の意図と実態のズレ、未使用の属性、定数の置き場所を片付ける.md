# TODO-082. import の意図と実態のズレ、未使用の属性、定数の置き場所を片付ける

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 19,702 / cache_creation 202,884 / 概算 $3.2 |
|      | main 70% + implementer 18% + verifier 6% + wording 6%（料金の割合） |

分担の理由と各担当の報告は [`archives/agents/TODO-082/`](../agents/TODO-082/README.md) にある。

## きっかけ

基本設計のレビュー（`docs/design-review.md` の H・J・K）で挙がった
細かい 7 件。TODO-081 で `CONF_KEY_LOAD_MONTHS` だけを移し、
残りをここで扱うと決めていた。

判断が要る点が 3 つ残っていたので、着手前に利用者へ聞いた。

1. **`__init__.py` の import はやめる。** `migrate.py` のコメントは
   変えない
2. **`_app` / `_req` と `filename` / `dirname` は消す。`get_keys()` は
   残す**
3. **`x_data1` は消す**

## やったこと

**挙動は変えていない**（`x_data1` を消したのだけが例外）。

### 1. `__init__.py` の re-export をやめた

`migrate.py` には「`handler.py` を import すると移行ツールが tornado に
依存してしまうので、設定ファイル名はここに持つ」と書いてあるのに、
`__init__.py` が `MainHandler` と `WebServer` を import していたため、
`ytsched migrate` は結局 tornado を読み込んでいた。

- `__init__.py` からクラス 5 つの import を消し、`__all__` を
  メタデータ 3 つ（`__author__` / `__prog_name__` / `__version__`）だけに
  した
- パッケージ経由で import していたのは `__main__.py` だけだった
  （tests・tools はすべてモジュール直指定）。`SchedDataFile` は
  `.ytsched` から、`WebServer` は `.webapp` から直接 import する形にした
- `migrate.py` のコメントは変えていない。これで実情と一致する
- `from ytsched.migrate import Migrator` のあと `"tornado" in sys.modules`
  が `False` になることを確かめた

### 2. 使われていない属性を消した

- `HandlerBase._app` / `_req` — 代入されるだけだった。直前の
  `__log.debug(f"app={app}")` は残した
- `SchedDataFile.filename` / `dirname` — `src` では未使用で、
  `tests/test_ytsched.py` の `test_date2path` がアサートしていただけ。
  アサート 2 行も一緒に消した。**これで `pathname.split("/")` による
  パスの分解ごと無くなったので、「`os.path` にする」も同時に片付いた**
  （`os.path` を新たに使う必要は無かった）
- `SchedData.get_keys()` は**残した**。`src` からの呼び出しは
  コメントアウトされたログだけだが、キャッシュの LRU 順を見る唯一の
  公開手段で、`test_get_sdf_lru_order` / `test_get_sdf_discard` が使う。
  消すと、テストが private の `_sdf_cache` を覗く形になる

### 3. `CONF_KEY_*` 3 つを `MainHandler` へ移した

`CONF_KEY_TODO_DAYS` / `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` を
`HandlerBase` から `MainHandler` の `CONF_KEY_LOAD_MONTHS` の隣へ移した
（TODO-081 と同じ形）。`CONF_KEY_SEARCH_STR` は `EditHandler.get()` でも
読むので `HandlerBase` に残した。

`tests/test_handler.py` がこの 3 つを使っていたが、あれは
`get_conf` / `set_conf` の読み書きそのものを見るテストで、キーが何かは
本質ではない。**`MainHandler` を import させず**、素の文字列
（`"ToDo_Days"` など）に置き換えた。

### 4. `__main__.py` の文字列と `x_data1`

- モジュールの docstring が `"""main for musicbox package"""`、
  `cli` グループの help が `sample package` と、別のプロジェクトからの
  写しだったので直した
- `x_data1` サブコマンドと、そこからしか使っていない `DataFileApp`
  クラス、余った `datetime` の import を消した。`ytsched --help` には
  `migrate` と `webapp` だけが並ぶ
- `--size_limit` の既定値だけ `100 * 1024 * 1024` の直書きだったので
  `WebServer.DEF_SIZE_LIMIT` にした（help の文字列は元からこちらを
  使っていた）。値は変わらない（`104857600`）

### 5. ruff の設定を `pyproject.toml` へ移した

`--line-length 78` と `--extend-select I` が `mise.toml` のコマンド行に
あり、`pyproject.toml` を見ても効いている規則が分からなかった。

- `[tool.ruff]` の `line-length = 78`、`[tool.ruff.lint]` の
  `extend-select = ["I"]` に移した
- `mise.toml` の `fmt` タスクと `docs/Developer.md` の個別コマンドの
  例からオプションを外した
- **移したのは置き場所だけで、規則は増やしていない**（`select` は
  足していないので、既定の `E4,E7,E9,F` に `I` が乗った状態のまま）

## テスト

- `mise run lint`（fmt・basedpyright・mypy）と `mise run test` —
  **475 passed**
- verifier が、79 文字の行と import 順の乱れを含む一時ファイルを作って、
  `line-length 78` と `I001` が `pyproject.toml` 側の設定で実際に効く
  ことを確かめた
- `ytsched --help` / `webapp --help` / `migrate --help` に `x_data1` も
  `musicbox` も `sample package` も出ないこと
- 一時ディレクトリを `--datadir` に指定して起動し、`/ytsched/` が 200 を
  返すこと

## 文書

`src/README.md` の CLI の説明から `x_data1` を消した。
`docs/Developer.md` の個別コマンドの例から ruff のオプションを外した。
