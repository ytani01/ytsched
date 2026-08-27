# TODO-081 reviewer 報告

## 確認した範囲

- `TODO.md` の TODO-081、`docs/design-review.md` の D・G
- `archives/agents/TODO-081/implementer-task.md` / `implementer-report.md`
- `git diff`（`src/README.md` / `edit_handler.py` / `handler.py` /
  `main_handler.py` / `webapp.py` / `tests/README.md` / `tests/helpers.py` /
  `tests/test_handler.py` / `tests/test_main_handler.py` / `tests/test_web.py`）と、
  未追跡の `src/ytsched/handler_util.py` / `tests/test_handler_util.py`
- `git show HEAD:src/ytsched/handler.py` と移した後の 5 関数を突き合わせ
- `app.settings`／`SEARCH_MODE_MAX_DAYS`／`CONF_KEY_*` の grep
- `ruff check` / `basedpyright` を対象ファイルに対して実行（0 件）

## 確信度の高い指摘

無し。

依頼の 1〜6 の観点をそれぞれ確かめたが、いずれも問題を見つけなかった。

1. `HandlerBase.__init__` は `self._sd` を使っておらず、`initialize()` は
   `self._sd` の設定だけを行う。tornado の `RequestHandler.__init__`
   （`.venv/.../tornado/web.py:212-242`）は末尾で
   `self.initialize(**kwargs)` を呼ぶ実装になっており、docstring の説明も
   実物と一致していた
2. `app.settings.get("sd")` / `app.settings["sd"]` の残存参照は
   `src/` `tests/` 全体に無かった（grep で確認）
3. 移した 5 関数（`convert_value` / `date_range` / `check_date` /
   `str2date` / `check_int_range`）を `git show HEAD:src/ytsched/handler.py`
   と 1 行ずつ突き合わせたが、ロジックは変わっていない。
   `SEARCH_MODE_MAX_DAYS` はクラス変数だったが、サブクラス
   （`MainHandler` / `EditHandler`）のどちらも上書きしておらず
   （grep で確認）、モジュール定数に変えても実質は変わらない
4. `tests/helpers.py` の `weakref.WeakKeyDictionary` について、依頼にあった
   代案 2 つを検討した。
   - **`Application` のサブクラスを作る案** は機能しない。
     `tornado.testing.AsyncHTTPTestCase.setUp()`（基底クラス）が
     `self._app = self.get_app()` を実行しており、`get_app()` の宣言は
     `def get_app(self) -> Application`。`self` の静的型は
     `AsyncHTTPTestCase` のまま解決されるため、`WebTestBase` 側で
     `get_app()` をオーバーライドしても `self._app` の型は
     `Application` に固定される。implementer の説明どおりで、確認できた
   - **`make_app()` が `(app, sd)` を返す案** も、`WebTestBase.get_app()`
     （`tests/test_web.py:147`）が `tornado.testing` の決まりで
     `Application` 単体を返す必要があるため、そのままは使えない
   - 上記から、`weakref.WeakKeyDictionary` を挟む今回の実装は妥当と判断する
5. `handler_util.py` は `click_utils.py`（対象名 + `_util`）に揃えており、
   既存の並びと矛盾しない
6. ログは `_log = getLogger(__name__)`。`migrate.py`（クラスの無い
   モジュール）の前例に倣っており、`CLAUDE.md` の「クラス本体に
   `__log = getLogger(__qualname__)`」はクラスがある場合の決まりなので
   矛盾しない。`handler.py` の docstring と `src/README.md`
   （クラス図・説明文）も実体に合わせて直っている

## 確信度の低い指摘（気になる点）

- `tests/helpers.py` の `_APP_SD` はモジュールレベルのグローバルな
  可変辞書。`weakref` を使っているのでエントリは `app` の GC に追随して
  消え、実害は無いと考えるが、テストプロセスの短い寿命を考えると
  素の `dict` でも実質的な違いは無い。`weakref` を選んだこと自体は
  安全側であり問題視するほどではないが、選んだ理由（GC 追随の必要性）が
  報告に書かれていなかった点は気になった
- `app_sd()` は `make_app()` を経由しない `Application` を渡すと
  `KeyError` になる。テスト用の補助関数なので許容範囲だが、
  エラーメッセージが素の `KeyError`（渡した `app` の情報を含まない）に
  なる点は、デバッグ時にやや不親切かもしれない

いずれも「直すべき」ではなく「気になる」程度。

## 判断が要る点（main 向け）

- 依頼の 4 で挙げられていた 2 つの代案は、いずれも `tornado.testing` の
  制約により機能しないことを確認できた。`weakref.WeakKeyDictionary`
  を使う実装のままで良いと考える
