# TODO-036 implementer への依頼

`src/ytsched/click_utils.py`（新規・未コミット）を `__main__.py` から使うようにする。
方針は利用者との相談で決まっている。**方針そのものは変えないこと。**
疑問があれば実装を止めて報告する。

## やること

### 1. `src/ytsched/click_utils.py` に型ヒントを付ける

中身の動きは変えない。このリポジトリの `ruff` / `basedpyright` / `mypy` が
通るところまで型ヒントを足す。`func` はデコレータが受け取る任意の呼び出し可能
オブジェクトなので、`Callable[..., Any]` 相当で構わない。

### 2. `__main__.py` で `click_common_opts` を使う

`cli` グループと 3 つのサブコマンド（`x_data1` / `migrate` / `webapp`）すべてに
付ける。

- `ver_str` には `ytsched.__version__` を渡す
- 手書きの `--debug` / `-d` オプション 3 箇所を消す（`click_common_opts` が付ける）
- `cli` の `CONTEXT_SETTINGS`（`help_option_names`）は要らなくなるので消す。
  `click_common_opts` が各コマンドに `help_option` を付ける
- `click_common_opts` は最後に `click.pass_context` を適用する。**各コマンド関数の
  第 1 引数に `ctx` を足すこと。** `cli` に元からある `@click.pass_context` は
  外す（二重に付くため）
- `webapp` の `--version` / `-v`（`version` フラグを `WebServer` に渡していたもの）は
  消し、`click_common_opts` の `version_option` に任せる

### 3. `WebServer` の `version` 引数を消す

`src/ytsched/webapp.py`:

- `__init__` の `version: bool = False` 引数と、docstring の該当行を消す
- コンストラクタ内の `if version: print(...); sys.exit(0)` を消す
- `__main__.py` の `WebServer(...)` 呼び出しから `version` を外す
- **`tornado.web.Application` に渡している `version=VERSION` は消さない**
  （テンプレートが使っている）。`VERSION` / `PROG_NAME` / `AUTHOR` / `sys` の
  import が未使用にならないか確認し、未使用になったものだけ消す

## 確かめること

`mise run fmt` → `mise run lint` → `mise run typecheck` → `mise run test` を通す。
（`mise run upgradeproject` は**走らせない**）

加えて、次が実際に動くことを自分でも見ておく（`--datadir` には必ず一時
ディレクトリを指定する）:

- `uv run ytsched --version` / `-V` / `-v`
- `uv run ytsched --help` / `-h`
- `uv run ytsched webapp --help`
- `uv run ytsched migrate --help`

## 報告

`archives/agents/TODO-036/implementer-report.md` に書く。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
