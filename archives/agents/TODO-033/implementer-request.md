# TODO-033 implementer への依頼

`WebServer.URL_PREFIX` が `DEF_URL_PREFIX` に改名されたのに追随できて
いない 3 か所を直してほしい。**機械的な置き換えで済むはず。**

## 読むもの

- `TODO.md` の `TODO-033` の節（背景）

## 直すもの

| 場所 | 内容 |
|---|---|
| `tests/helpers.py:23` | `URL_PREFIX = WebServer.URL_PREFIX` |
| `tests/test_webapp.py:30,34` | `WebServer.URL_PREFIX` を直に参照 |
| `src/README.md:67` | 説明が `WebServer.URL_PREFIX` のまま |

`src/ytsched/webapp.py:34` の定義は `DEF_URL_PREFIX = "/ytsched"`。
`WebServer.__init__()` は `url_prefix: str = DEF_URL_PREFIX` を引数に
取るようになっている（`2b4fcce feat(webapp): add url_prefix option`）。

**`tests/helpers.py` の `URL_PREFIX`（モジュールの変数名）はそのままで
よい。** 右辺の `WebServer.URL_PREFIX` を `WebServer.DEF_URL_PREFIX` に
するだけ。この変数名は `test_handler.py` / `test_web.py` /
`test_main_handler.py` から import されていて、そちらまで直すと差分が
無駄に大きくなる。

**`src/README.md:67` は、今の実物に合わせて書き直す。** 今は
「URL は `/ytsched`（`WebServer.URL_PREFIX`）配下」となっているが、
`--url-prefix` で変えられるようになったので、既定値であることが
分かる書き方にする（`WebServer.DEF_URL_PREFIX`）。1 行で済ませ、
**周りの文には手を入れないこと**。

## 確かめること

- `uv run pytest tests` が**テストを集められる**ようになり、全件通ること
- `uv run ruff format --line-length 78 src tests` /
  `uv run ruff check --extend-select I src tests` /
  `uv run basedpyright src tests` / `uv run mypy src tests`

**通らないテストがあったら、直さずに報告すること。**
この作業ツリーには TODO-027 の未コミットの変更が入っている。
TODO-027 側の不具合が出たら、それはこの項目の範囲外。

## 決まりごと

- **作業ツリーを戻すコマンド（`git checkout` / `git restore` /
  `git stash`）は絶対に使わない。** TODO-027 の未コミットの変更が
  消える
- **`mise run upgradeproject` は走らせない**
- 実データ（`~/ytsched/data`）には触らない
- 報告は `archives/agents/TODO-033/implementer-report.md` に書く。
  返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内
