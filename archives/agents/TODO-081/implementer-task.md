# TODO-081 implementer への依頼

`TODO.md` の TODO-081 と `docs/design-review.md` の D・G を先に読むこと。

**挙動は変えない。** HTML の出力も、エラーの返し方も今までどおりにする。

## やること

### 1. 引数と設定値の変換・検証を `HandlerBase` から出す

`src/ytsched/handler.py` にある次の 5 つは、`self` をログにしか使って
いない純粋な関数で、`RequestHandler` を継承していることと関係が無い。

- `convert_value()` / `date_range()` / `check_date()` / `str2date()` /
  `check_int_range()`
- 定数 `SEARCH_MODE_MAX_DAYS`（`date_range()` が使う）

**新しいモジュール 1 つへ、モジュール直下の関数として出す。**

- ファイル名は既存の並び（`ytsched.py` / `handler.py` /
  `main_handler.py` / `edit_handler.py` / `webapp.py` / `migrate.py` /
  `mylog.py` / `click_utils.py`）に釣り合うものにする。
  名前は自分で決めてよいが、報告に理由を書くこと
- ログは `mylog.py` の `getLogger(__name__)` を使う
  （クラスが無いので `__qualname__` ではない。**`CLAUDE.md` のログの
  決まりを読んでから書くこと**）
- **`HandlerBase` に転送用のメソッドを残さない。** 呼ぶ側を直す
- 呼んでいるのは `main_handler.py` / `edit_handler.py` /
  `handler.py` 自身と、テスト 2 ファイル（全部で 47 か所）。
  grep で全部拾ってから直すこと

### 2. `SchedData` を `initialize()` で渡す

いまは `webapp.py` が `tornado.web.Application` の設定に `sd=self._sd`
を入れ、`HandlerBase.__init__` が `app.settings.get("sd")` で取り出して
いる。このため `self._sd` の型が `Any` になり、型チェッカが
`SchedData` として見られない。

- `webapp.py` の URL の登録を
  `(path, MainHandler, {"sd": self._sd})` の形にする（4 か所）
- `HandlerBase` に `initialize(self, sd: SchedData) -> None` を足し、
  `self._sd: SchedData = sd` とする。`__init__` の
  `app.settings.get("sd")` は消す
- `app.settings` の `sd` も消す（他から使っていないか grep すること）
- **`initialize()` は `__init__` のあとに呼ばれる。** `__init__` の中で
  `self._sd` を使っていないことを確かめてから移すこと
- `tests/helpers.py` の `make_app()` / `make_handler()` も直す。
  ここが直らないとテストが全部落ちる

`title` / `author` / `version` / `url_prefix` / `datadir` は
**今回は動かさない**（`sd` だけ）。範囲を広げない。

### 3. 定数の置き場所のズレ

- `CONF_KEY_LOAD_MONTHS` は `MainHandler` しか使っていないので
  `MainHandler` へ移す（grep で確かめること）
- 他の `CONF_KEY_*` も同じように片方しか使っていないものがあれば、
  **報告に挙げるだけ**にして動かさない（この項目で動かすのは
  `CONF_KEY_LOAD_MONTHS` だけ）
- `SEARCH_MODE_MAX_DAYS` は 1 で出したモジュールへ移る

## 気をつけること

- **例外とログの出方を変えない。** `convert_value()` が警告を 1 行出して
  `None` を返す挙動（TODO-027・TODO-012）はそのまま
- `handler.py` に残るのは「`conf.json` の読み書き」だけになるはず。
  クラスの docstring と `src/README.md` の説明を、それに合わせて直す

## テスト

- 既存のテストが全部通ることが第一。移した関数のテストは、
  ハンドラを組み立てずに呼べるようになるので、**そう書き直す**
  （`tests/test_handler.py` / `tests/test_main_handler.py`）
- 新しいモジュールのテストファイルを作るかどうかは自分で決めてよい。
  決めた理由を報告に書くこと。`tests/README.md` も直す
- `tests/test_webapp.py` は `Application` の組み立てを見ているので、
  `sd` を設定から外したことで落ちるかもしれない。**観点を減らさずに**
  新しい形に直すこと

`mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
**`mise run upgradeproject` は走らせないこと。**
アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する。
