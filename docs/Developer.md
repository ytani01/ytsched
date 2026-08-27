# 開発者向けドキュメント

開発環境の用意、開発ツールの使い方、テストとログの決まりをまとめる。
利用者向けの説明は [../README.md](../README.md)、ソースコードの構成は
[../src/README.md](../src/README.md)、テストの構成は
[../tests/README.md](../tests/README.md)、データ形式は
[data-format.md](data-format.md) を見ること。

## 技術スタック

| もの | 何のためか |
| --- | --- |
| Python 3.14 | 実行環境。`pyproject.toml` の `requires-python` で固定 |
| [uv](https://docs.astral.sh/uv/) | パッケージ管理・仮想環境・実行（`uv run` / `uv sync` / `uv build`） |
| [tornado](https://www.tornadoweb.org/) | Web サーバとテンプレートエンジン |
| [click](https://click.palletsprojects.com/) | CLI（`ytsched` コマンド）の組み立て |
| [loguru](https://github.com/Delgan/loguru) | ログ（`mylog.py` がラップしている） |
| [pytest](https://docs.pytest.org/) | テスト |
| [ruff](https://docs.astral.sh/ruff/) | フォーマットと lint |
| [basedpyright](https://docs.basedpyright.com/) / [mypy](https://mypy-lang.org/) | 型チェック（2 つともかける） |
| [mise](https://mise.jdx.dev/) | タスクランナー（`mise.toml`） |

## 開発環境の用意

Python 3.14 以上と uv があれば足りる。

```sh
git clone https://github.com/ytani01/ytsched.git
cd ytsched
uv sync
```

`uv sync` で `dependency-groups.dev`（pytest・ruff・basedpyright・mypy
など）も一緒に入る。以降のコマンドは `uv run` 経由か、`mise run` で
タスクとして叩く。

## mise のタスク

`mise.toml` に定義がある。`build` は `test` に、`test` は `lint` に、
`lint` は `fmt` と `typecheck` の両方に依存する。

```sh
mise run fmt        # ruff format / ruff check --fix
mise run typecheck  # basedpyright / mypy
mise run lint       # fmt と typecheck の両方
mise run test       # pytest（lint に依存）
mise run build      # uv build（test に依存）
```

アプリを動かすタスクもある。引数は `--` のあとに書く（mise が行の末尾へ
足す）。

```sh
mise run webapp                            # ~/ytsched/data・port 10085
mise run webapp -- --datadir /tmp/x --port 10099
mise run migrate -- --dry-run
mise run tokens -- TODO-046                # TODO 項目ごとのトークン消費量
mise run shot -- --open                    # 画面を撮る
```

`upgradeproject`（`uppj`）は依存を上げ直すタスクで、`lint` などからは
呼ばれていない（**どこからも依存されていない**）。`rm -f uv.lock` →
`uv sync` → `uv pip install -U` が走るので、上げ直したいときに明示的に
叩く。

## 個別コマンドで実行する場合

```sh
uv run pytest tests
uv run ruff format src tests tools
uv run ruff check --fix src tests tools
uv run basedpyright src tests tools
uv run mypy src tests tools
```

アプリの起動:

```sh
uv run ytsched webapp --datadir ~/ytsched/data --port 10085
```

旧形式（タブ区切り `.cgi`）から JSON Lines への移行
（`ytsched migrate`、オプションは [data-format.md](data-format.md) 参照）:

```sh
uv run ytsched migrate --datadir ~/ytsched/data
```

## 画面を撮る

見た目を変えたときは、テストだけでは確かめられない。`tools/screenshot.py`
で画面を撮る（TODO-046）。**先にアプリを起動しておくこと。実データを
汚さないよう、確かめるときは `--datadir` に一時ディレクトリを指定する。**

```sh
uv run ytsched webapp --datadir /tmp/x --port 10085 &
mise run shot -- --open -p todo046
```

保存先は既定で `~/tmp/playwright-mcp/`、ファイル名は
`{prefix}_{closed|open}_{幅}.png`。幅は既定で 412px（スマホ）と 800px の
2 つで、`-w` を複数回渡せば変えられる。`--open` を付けると、詳細（detail）
のような開閉するものを開いた状態も撮る（開くものは `--toggle` で指定。
既定は `input.longtext-sw`）。

- 撮る URL は既定で `http://localhost:10085/ytsched/`。`--urlprefix` の
  既定（`/ytsched`）に合わせてある。一覧は `/` にも割り当ててあるので
  どちらでも出るが、編集画面は前置きが無いと 404 になる。位置引数で
  変えられる（`mise run shot -- http://localhost:10086/`）
- playwright は dev 依存に入っている（TODO-056 でブラウザを動かす
  テストを足したときに入れた）。`uv sync` すれば `mise run shot` も
  そのまま動く
- ブラウザはシステムの `/usr/bin/chromium` を使う。
  `~/.cache/ms-playwright` にあるビルドは playwright-mcp が入れたもので、
  `--with playwright` が取ってくる版とは合わず起動しない（TODO-045）
- **HTTP のステータスが 200 以外なら、撮らずに終了コード 1 で終える**
  （TODO-053）。URL を間違えて 404 のページを撮ってしまい、変更の前後の
  突き合わせで見分けが付かなくなるのを防ぐため。

  ```sh
  $ mise run shot -- http://localhost:10085/edit/
  404: http://localhost:10085/edit/
  URL を確かめる。
  $ echo $?
  1
  ```

## テストの走らせ方

`tests/` はいずれも `uv run pytest tests`（または `mise run test`）で
まとめて動く。各テストファイルが何を見ているか、`helpers.py` の役割、
ゴールデンマスターテストの位置づけは [../tests/README.md](../tests/README.md)
を見ること。

`test_browser.py` だけはブラウザを起動する（TODO-056）。`pytest` は
`static/js/` のスクリプトを実行しないので、JavaScript の不具合は
それ以外のテストでは捕まらない。

- **他のテストと同じ `mise run test` で一緒に走る。** playwright は
  dev 依存に入れてあるので、`uv sync` のほかに用意するものは無い
- ブラウザはシステムの `/usr/bin/chromium` を使う（`mise run shot` と
  同じ理由。TODO-045）。無ければ skip する
- テストごとに `ytsched webapp` を空いている port で起動し、`--datadir`
  には `tmp_path` を渡す。実データ（`~/ytsched/data`）には触れない
- 1 件だけ走らせるときは
  `uv run pytest tests/test_browser.py -v`。ブラウザの動きを目で見たい
  ときは、`page` fixture の `launch()` に `headless=False` を足す

移行元（旧形式）の合成テストデータを作り直したいときは、
`uv run python tests/make_test_data.py` を実行する。

## ログの書き方

`mylog.py` のラッパを使う。標準の `logging` は使わない。クラス本体に
`__log = getLogger(__qualname__)` を 1 つ置く。

```python
from .mylog import getLogger


class SchedDataEnt:
    # クラス本体に置く（アンダースコア2つ）。__qualname__ はクラス名。
    __log = getLogger(__qualname__)

    def is_todo(self):
        self.__log.debug("SchedDataEnt.is_todo")
```

クラスの無いモジュール（`main` など）は、モジュール先頭に
`_log = getLogger("main")` のように置く。詳しいサンプルは
`src/ytsched/mylog.py` の docstring にある。

## memo

### JavaScript `Date` の罠

`new Date()` の日付の区切り文字が
`/` だと JST（+09:00）、`-` だと UTC とみなされる。

```
> (new Date("2021/01/01")).toISOString();
"2020-12-31T15:00:00.000Z"
> (new Date("2021-01-01")).toISOString();
"2021-01-01T00:00:00.000Z"
```

### JavaScript scroll・size 関連

![](javascript-scroll.svg)
