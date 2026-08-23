# TODO-031 verifier 報告

## 1. Mermaid として実際にパース・描画できるか

`~/work/ytsched` には何も足していない。scratchpad
（`/tmp/claude-649/.../scratchpad/mermaid-test/`）に `npm install mermaid
playwright-core`（mermaid 11.17.0）し、`git diff` から 4 つの図のソースを
そのまま抜き出した（`graphs/graph1.mmd`〜`graph4.mmd`）。

Node から `mermaid.esm.mjs` を `<script type="module">` で読み込む HTML を
作り、`python3 -m http.server` で配ってから（`file://` は ESM の CORS で
弾かれたため）、`~/.cache/ms-playwright/chromium-1200/chrome-linux/chrome`
を playwright-core で起動して `mermaid.parse()` と `mermaid.render()` の
両方を 4 図それぞれに対して呼んだ。

結果、**4 つとも `mermaid.parse()` が成功し、`mermaid.render()` も
例外を出さずに SVG まで作れた**（コンソール・ページエラーは 404 の
リソース読み込み 1 件のみで、図とは無関係）。

- graph1（`src/README.md` データモデルの classDiagram）: ○
  （`sde : list~SchedDataEnt~` のジェネリック記法、`-_sdf_cache :
  OrderedDict` の先頭アンダースコアも問題なし。SVG 37,980 文字）
- graph2（`src/README.md` Web ハンドラの classDiagram）: ○
  （`<<tornado.web>>` のステレオタイプ、および疑っていた
  `WebServer ..> MainHandler : "/", url_prefix, url_prefix/` の
  ダブルクォート・カンマ入りエッジラベルも問題なし。SVG 34,509 文字）
- graph3（`src/README.md` sequenceDiagram）: ○（SVG 32,635 文字）
- graph4（`docs/data-format.md` graph TD）: ○（SVG 32,459 文字）

## 2. 図の内容とコードの突き合わせ

`src/ytsched/ytsched.py`・`handler.py`・`main_handler.py`・
`edit_handler.py`・`webapp.py`・`migrate.py` を実際に読んで突き合わせた。

- `SchedDataEnt` の属性（`sde_id`/`date`/`time_start`/`time_end`/`type`/
  `title`/`place`/`detail`）は実在する
- `SchedDataFile` の `date`/`topdir`/`pathname`/`sde`（`list[SchedDataEnt]`
  相当）と `load()`/`save()`/`add_sde()`/`del_sde()`/`get_sde()` は実在する
- `SchedData` の `_sdf_cache`（`OrderedDict[..., ...]` 型）と `get_sdf()`/
  `get_sde()`/`add_sde()`/`del_sde()` は実在する
- `HandlerBase` の `load_conf`/`save_conf`/`get_conf`/`set_conf`/
  `convert_value`/`str2date`/`check_date`/`date_range` は実在する。
  `check_int_range` は実在するが図には無い ─ これは「詰め込みすぎない」
  意図的な省略として報告書に書かれているとおりで問題ない
- `EditHandler` に `post()` があり、中身は `self.get()` を呼ぶだけ。
  `MainHandler.post()` も `self.__log.debug(...)` のあと `self.get()` を
  呼ぶだけ。図の「post() は get() に委譲するだけ」は両クラスとも正しい
- `WebServer` が `tornado.web.Application` に渡す URL 一覧
  （`webapp.py` 96〜103 行）は、`r"/"`・`url_prefix`・`url_prefix/` が
  `MainHandler`、`url_prefix/edit`・`url_prefix/edit/` が `EditHandler`
  で、図のラベルと一致する。`WebServer` の公開メソッドは `main()` のみ
  （`__init__` はコンストラクタなので図に出ないのは通常の描き方）
- sequenceDiagram の `Note over Handler: __init__ のたびに Conf.cgi を
  読む (load_conf)` は、`handler.py` の `HandlerBase.__init__()`
  （67 行）が直接 `self._conf = self.load_conf()` を呼んでおり、
  `initialize()` や `get()` の中ではない。図の記述は正しい
- `docs/data-format.md` の graph の分岐は `migrate.py` の実装と一致。
  `ENCODINGS = ("utf-8", "euc_jp")` → 両方だめなら
  `FALLBACK_ENCODING`（euc_jp）を `errors="replace"` で読む
  （`decode_line()`）。`N_FIELD = 7` に対して `len(field) < N_FIELD` は
  空文字で埋め、`len(field) > N_FIELD` は超過分を `detail` の続きに
  つなぐ（`split_fields()`）。図の分岐条件・処理内容とも一致

食い違いは見つからなかった。

## 3. 既存のテスト

`mise run test` を実行。`ruff format`/`ruff check`/`basedpyright`/`mypy`
はすべて問題なし、`pytest` は **404 件 passed**（`mise run
upgradeproject` は走らせていない）。

```
============================= 404 passed in 2.84s ==============================
```

## 判断が要る点

無し。3 項目とも問題は見つからなかった。
