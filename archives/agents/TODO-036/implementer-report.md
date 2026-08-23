# TODO-036 implementer 報告

## 変更したファイル

- `src/ytsched/click_utils.py`（新規・未コミットだったもの / 型ヒントを追加）
  - `Func = Callable[..., Any]` / `Decorator = Callable[[Func], Func]` の別名を
    ファイル先頭に置き、`click_common_opts` の戻り値を `-> Decorator`、
    内側の `_decorator(func: Func) -> Func`、`decorators: list[Decorator]` と
    注釈した。**中身の動きは変えていない**（`~/work/tmr` 版と行の並びは同じ）
- `src/ytsched/__main__.py`
  - `from . import (..., __version__)` と `from .click_utils import
    click_common_opts` を追加
  - `CONTEXT_SETTINGS`（`help_option_names`）を削除
  - `cli` の `@click.pass_context` を `@click_common_opts(__version__)` に
    差し替え、`def cli(ctx, debug)` に
  - `x_data1` / `migrate` / `webapp` の手書き `--debug` / `-d` を消し、
    `@click_common_opts(__version__)` に差し替え。各関数の第 1 引数に `ctx` を追加
  - `webapp` の `--version` / `-v` オプションと、`WebServer(...)` へ渡していた
    `version` 引数を削除
- `src/ytsched/webapp.py`
  - `WebServer.__init__` の `version: bool = False` 引数と、docstring の
    `version: bool` の行を削除
  - コンストラクタ内の `if version: print(...); sys.exit(0)` を削除
  - 未使用になった `import sys` を削除（`sys` は他に使われていないことを
    grep で確認）
  - `tornado.web.Application(..., version=VERSION)` と `PROG_NAME` /
    `AUTHOR` / `VERSION` の import は**そのまま残した**（テンプレート用）

## 自分で確かめたこと

- `mise run fmt` → ruff format で 1 ファイル整形、`ruff check` は All checks passed
- `mise run typecheck` → basedpyright 0 errors / mypy Success (20 files)
- `mise run test` → 412 passed
- CLI の実挙動（`--datadir` にはすべて `mktemp -d` の一時ディレクトリを指定）
  - `uv run ytsched --version` / `-V` / `-v` → いずれも
    `ytsched 0.1.1.dev6+g061772762`
  - `uv run ytsched --help` / `-h` / 引数なし → ヘルプに
    `-V, -v, --version` / `-d, --debug` / `-h, --help` が並ぶ。
    サブコマンド一覧（migrate / webapp / x-data1）も出る
  - `uv run ytsched webapp --help` / `migrate -h` / `x-data1 -h` → 3 つとも
    共通オプションが付いている。`webapp` から `--version` の重複は消えている
  - `uv run ytsched webapp -V` / `migrate -v` → バージョンを表示して終了
  - `uv run ytsched migrate -d --dry-run` → DEBUG ログが出る。`-d` 無しでは
    出ない（`--debug` が効いている）
  - `uv run ytsched x-data1 2021 1 1 --datadir <tmp> -d` → DEBUG ログが出る
  - `uv run ytsched webapp --datadir <tmp> --port 10199` を起動し、
    `curl http://localhost:10199/ytsched` が **200**。テンプレートが使う
    `version` は Application 側に残っているので描画も問題なし

## 単独で決めた判断

1. **`cli`（グループ）に `loggerInit(debug=debug)` を足した。**
   `click_common_opts` がグループにも `--debug` を付けるのに、受けた
   `debug` を誰も使わないと `ytsched --debug` が黙って無視されるため。
   `~/work/tmr` の `cli` も同じく `loggerInit(debug)` を呼んでいるので、
   そちらに揃えた。サブコマンド側でも `loggerInit(debug=debug)` を呼ぶので、
   `ytsched --debug migrate`（グループ側だけに `-d`）はサブコマンドの
   `loggerInit(debug=False)` で上書きされ、DEBUG は出ない。これは tmr と
   同じ挙動。**依頼書に無い追加なので、不要なら消してよい。**
2. **`click_utils.py` に型の別名（`Func` / `Decorator`）を置いた。**
   同じ長い `Callable[..., Any]` が 4 箇所に出て 78 桁に収まらなくなるため。
   tmr 版との差は型注釈だけに保った。

## 気づいたが直さなかったもの

- **`--version` の表示が `ytsched <ver>` で、`Ytsched <ver>` ではない。**
  TODO-036 の節には「表示は `Ytsched <ver>` になり」とあるが、実際には
  `%(prog)s` に入るのが console script 名の `ytsched` なので小文字になる。
  `__prog_name__`（`"Ytsched"`）が使われるのは
  `python -m ytsched`（`cli(prog_name=__prog_name__)`）の経路だけ。
  表示を `Ytsched` に揃えるなら `pyproject.toml` の entry point 側か
  `version_option` の `prog_name` 指定が要るので、**main の判断待ちとして
  手を付けていない**（TODO-036 の範囲内の話だが、方針を変える判断になるため）。
- `__main__.py` の関数には型ヒントが無い（`DataFileApp.__init__`、各コマンド
  関数）。TODO-036 の範囲外なので触っていない。
- `cli` の help 文が `sample package` のまま（雛形の名残）。範囲外。
- `webapp` の `--size_limit` は `default=100 * 1024 * 1024` の直値で、help は
  `WebServer.DEF_SIZE_LIMIT` を参照している（値は一致）。範囲外。

## うまくいかなかったところ

特になし。fmt / lint / typecheck / test と手動確認はすべて通った。

---

## 追加対応（グループ側の `--debug` をサブコマンドへ引き継ぐ）

利用者の判断を受けての追加。`--version` の表示（`ytsched <ver>` の小文字）は
指示どおり手を付けていない。`click_utils.py` も変更していない。

### 変更したファイル

- `src/ytsched/__main__.py` のみ
  - モジュール直下に `_is_debug(ctx, debug)` を追加。`ctx.obj` が dict の
    ときだけ `ctx.obj.get("debug", False)` を見て、自分の `debug` との
    どちらかが立っていれば `True` を返す。`ctx.obj` が `None`（`cli` を
    経由しない呼び出し）でも落ちない
  - `cli` の冒頭で `ctx.ensure_object(dict)` → `ctx.obj["debug"] =
    bool(debug)`
  - `x_data1` / `migrate` / `webapp` の `loggerInit(debug=debug)` の直前に
    `debug = _is_debug(ctx, debug)` を入れた。`webapp` はこの後で
    `WebServer(..., debug=debug)` に渡すので、まとめた値がそのまま伝わる

### 確かめたこと

- `mise run fmt`（ruff format: 23 files unchanged / check: All checks passed）
  → `mise run typecheck`（basedpyright 0 errors、mypy Success 20 files）
  → `mise run test`（412 passed）
- `--datadir` に `mktemp -d` の一時ディレクトリを指定して、DEBUG 行数を数えた
  - `ytsched --debug migrate --dry-run` → DEBUG 3 行（出る）
  - `ytsched migrate -d --dry-run` → DEBUG 3 行（出る）
  - `ytsched --debug migrate -d --dry-run` → DEBUG 3 行（出る）
  - `ytsched migrate --dry-run` → DEBUG 0 行（出ない）
- `ytsched --debug x-data1 2021 1 1 --datadir <tmp>` → DEBUG 6 行（出る）
- `ytsched --debug webapp --datadir <tmp> --port 10198` → DEBUG が出るうえ、
  Application の設定が `'debug': True` / `'autoreload': True` になっており、
  `WebServer` にも引き継がれていることを確認
- `cli` を経由せずコマンド関数を直接呼ぶ経路は無いことを確認（`tests/` と
  `tools/` を grep。`cli(` / `x_data1` / `migrate(` の直接呼び出しは無し。
  entry point は `ytsched.__main__:cli` のみ）

### 判断

- `_is_debug()` はモジュール直下の非公開関数にした。3 つのサブコマンドで
  同じ 1 行を書くだけなので、クラスや `click_utils.py` 側には持たせていない
  （`click_utils.py` は変更しない指示のため）。
- `ctx.obj` の判定は `isinstance(ctx.obj, dict)` にした。`None` のときも、
  将来 dict 以外が入ったときも落ちない。
