# TODO-081. ハンドラの役割と、依存の渡し方を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 25,175 / cache_creation 699,296 / 概算 $9.0 |
|      | main 64% + implementer 26% + reviewer 4% + verifier 4% + wording 2%（料金の割合） |

分担の理由と各担当の報告は [`archives/agents/TODO-081/`](../agents/TODO-081/README.md) にある。

## きっかけ

基本設計のレビュー（`docs/design-review.md` の D・G）で挙がった 2 件。

`handler.py` にあったのは「`conf.json` の読み書き」「引数と設定値の
変換・検証」「表示に使える日付の範囲」の 3 つ。後ろの 2 つは `self` を
ログにしか使わない純粋な関数で、`RequestHandler` を継承していることと
関係が無い。それでもテストを書くにはハンドラを組み立てる必要があった。

依存は `tornado.web.Application` の設定に入れて `app.settings.get("sd")`
で取り出していたため、`self._sd` の型が `Any` になり、型チェッカが
`SchedData` として見られなかった。

## やったこと

**挙動は変えていない。**

### 1. `handler_util.py` を作った

`convert_value()` / `date_range()` / `check_date()` / `str2date()` /
`check_int_range()` と定数 `SEARCH_MODE_MAX_DAYS` を、モジュール直下の
関数として `src/ytsched/handler_util.py` へ出した。

- **名前は `click_utils.py` の並び**（対象名 + `_util(s)`）に揃えた
- ログは `_log = getLogger(__name__)`。クラスが無いので `__qualname__`
  ではない（`migrate.py` と同じ書き方）
- **`HandlerBase` に転送用のメソッドを残していない。** 呼んでいた
  `main_handler.py` / `edit_handler.py` と、テスト 3 ファイルを直した
- `SEARCH_MODE_MAX_DAYS` はクラス変数だったが、`MainHandler` /
  `EditHandler` のどちらも上書きしていないので、モジュール定数にした

### 2. `SchedData` を `initialize()` で渡すようにした

- `webapp.py` の URL 登録 5 か所を `(path, MainHandler, {"sd": self._sd})`
  の形にし、`Application` の設定から `sd` を外した
- `HandlerBase` に `initialize(self, sd: SchedData) -> None` を足し、
  `self._sd: SchedData = sd` とした。`__init__` は `**kwargs` を
  `super().__init__()` へ転送するだけになった（tornado の
  `RequestHandler.__init__` が末尾で `self.initialize(**kwargs)` を呼ぶ）
- `self._sd` に `SchedData` の型が付いた

`title` / `author` / `version` / `url_prefix` / `datadir` は動かして
いない（`sd` だけ）。

### 3. `CONF_KEY_LOAD_MONTHS` を `MainHandler` へ移した

`HandlerBase` にありながら `MainHandler` からしか使っていなかった。

**`CONF_KEY_TODO_DAYS` / `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` も
同じズレがある**（`MainHandler` からしか使っていない）が、今回は動かさ
なかった。`CONF_KEY_SEARCH_STR` だけは `EditHandler.get()` でも読んで
いるので `HandlerBase` のままで妥当。

## テストの `sd` の受け渡し

`app.settings` から `sd` を外したので、テスト側で `app` から
`SchedData` を引く手立てが要る。`tests/helpers.py` に
`weakref.WeakKeyDictionary` で持たせ、`app_sd(app)` で引く形にした。

素直に見える代案は 2 つとも使えないことを reviewer が確かめている。

- **`app.sd = sd` と動的属性を生やす案**：`self._app`
  （`tornado.testing` 由来）の静的型が `tornado.web.Application` の
  ままなので、`basedpyright` が `reportAttributeAccessIssue` で落ちる。
  `Application` のサブクラスを作って `get_app()` を上書きしても、
  `AsyncHTTPTestCase.setUp()` の `self._app = self.get_app()` は
  基底クラス側の宣言（`-> Application`）で解決されるため型は変わらない
- **`make_app()` が `(app, sd)` を返す案**：`WebTestBase.get_app()` は
  `tornado.testing` の決まりで `Application` 単体を返す必要がある

## テスト

- `tests/test_handler_util.py`（新規）— 移した 5 関数を、ハンドラを
  組み立てずに直接確かめる。成功・`ValueError`・範囲の境界。
  **移す前はこれらを単体で見るテストが無く**、`test_web.py` の
  HTTP 経由の間接テストだけだった
- `tests/helpers.py` の `make_app()` / `make_handler()` を新しい形に、
  `test_handler.py` / `test_main_handler.py` / `test_web.py` の
  `app.settings["sd"]` と `MainHandler.SEARCH_MODE_MAX_DAYS` の参照を直した
- `tests/test_webapp.py` は `sd` をアサートしていなかったので、直す
  必要は無かった
- `mise run fmt` / `typecheck` / `lint` / `test` — 警告・エラー無し、
  **475 passed**（`test_browser.py` の 19 件を含む）
- verifier が、一時ディレクトリで実際に起動して 5 つの URL すべてが
  200 を返すこと、予定の追加・修正・削除が動くこと、
  `convert_value()` が警告を 1 行出して無視する挙動（TODO-027・
  TODO-012）が変わっていないことを確かめた

## 文書

`src/README.md` のモジュール一覧・クラス図・説明文と、
`tests/README.md` を、上記に合わせて直した。
