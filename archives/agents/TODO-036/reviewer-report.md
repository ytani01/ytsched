# TODO-036 reviewer 報告

対象: `src/ytsched/click_utils.py`（新規）、`src/ytsched/__main__.py`、
`src/ytsched/webapp.py`（いずれも未コミット）。

**結論: 動作を壊す欠陥は見つからなかった。** 依頼書の「見てほしいところ」
5 点はいずれも問題なしと判断した（根拠は下記）。直すべきものとして挙げるのは
文書の追随漏れ 1 件だけ。

---

## 1. 直すべき

### 1-1. `src/README.md` のモジュール一覧に `click_utils.py` が無い

`src/README.md` の「モジュール一覧」（`src/ytsched/` のツリー）に、今回
追加した `click_utils.py` が入っていない。`src/README.md` は
「ソースコードの構成」を書く場所と `CLAUDE.md` で決めてあり、
`mylog.py` のような小さいモジュールも 1 行で載っている。**新しい
モジュールを足したのに一覧に無いのは、この文書の役割からの逸脱**。

`__main__.py` の行の近くに 1 行足せば済む。あわせて、その下の
「CLI には `webapp`…」の段落に、共通オプション（`-h` / `-d` / `-V` `-v`）が
全コマンドに付くこと、グループの `--debug` がサブコマンドへ引き継がれる
ことを 1〜2 行書いておくと、次に触る人が `_is_debug()` の意図を追いやすい
（こちらは任意）。

---

## 2. 判断が要る（main へ）

### 2-1. `TODO.md` の TODO-036 の記述と実際の表示が食い違ったまま

`TODO.md` 32 行目に「表示は `Ytsched <ver>` になり」とあるが、実際は
`ytsched <ver>`（小文字）。click の `version_option` は
`prog_name = ctx.find_root().info_name` を使い、entry point 名
（`pyproject.toml` の `ytsched = "ytsched.__main__:cli"`）が入るため。
小文字のままでよいと決まった以上、**archives へ移すときにこの行を実際に
合わせて書き直すか、「実際は小文字だった」と併記するか**を決めてほしい。
`__prog_name__ = "Ytsched"` が効くのは `python -m ytsched` の経路だけ、
という点も残しておくと後で迷わない。

### 2-2. `mylog.loggerInit()` の docstring「1 度だけ呼ぶ」が実態と合わなくなった

`src/ytsched/mylog.py` 110 行目:

> 各 CLI コマンドの先頭で 1 度だけ呼ぶ。

今回から `cli`（グループ）とサブコマンドの両方で呼ばれるので、1 回の実行で
**2 回**呼ばれる。

**動作上の実害は無い**と確認した:

- `loggerInit()` は `logger.remove()` → `logger.add()` なので、
  何度呼んでもシンクは 1 つ。二重出力にならない
- 名前ごとの水準（`_levels[name]`）は `loggerInit()` で消えない
  （`tests/test_mylog.py::test_getLogger_level_survives_loggerInit` が
  その保証）。上書きされるのは `_levels[""]` だけ
- グループのコールバックと、サブコマンドの `loggerInit()` の間でログを
  出しているコードは無い（`cli` の本体は `ctx.obj` の設定とヘルプ表示だけ）。
  そのため、グループ側だけ `debug=False` で初期化される区間に失われる
  DEBUG ログは無い

ただし docstring は事実と違うので、**「先頭で呼ぶ（何度呼んでも安全）」の
ように直すか、`cli` 側の `loggerInit()` をやめるか**を決めてほしい。
実装者の報告 50-59 行目にあるとおり、`cli` の `loggerInit()` は
「`ytsched --debug`（サブコマンド無し）を黙って無視しないため」に足された
もので、`_is_debug()` が入った今も、サブコマンド無しの経路では
これが唯一の初期化になっている（=消すなら別の手当てが要る）。

### 2-3. `click_utils.py` が `~/work/tmr` 版と同一ではなくなった

`diff ~/work/tmr/src/tmr/click_utils.py src/ytsched/click_utils.py` の
差は**型ヒントだけ**で、指示（「型ヒント以外は中身を変えない」）は守られて
いる。ロジックの行の並びも同じ。

一方で、「他のプロジェクトと共通のファイル」と言いつつ 2 つの写しが
ずれた状態になった。次に片方から片方へコピーしたときに、型ヒントが
落ちる／戻る事故が起きうる。**tmr 側へ型ヒントを持っていくか、
ずれたままにするか**を決めておくとよい（ytsched の範囲外なので、
ここでは指摘だけ）。

---

## 3. 依頼書の「見てほしいところ」への回答

いずれも**問題なし**と判断した。根拠を残す。

### 3-1. `_is_debug()` の作り

- `isinstance(ctx.obj, dict)` の判定は妥当。click の `Context.__init__` は
  `obj` 未指定なら親の `obj` を引き継ぐので、`cli` 経由なら必ず dict が入り、
  直接呼び出しなら `None` になる。どちらでも落ちない
- `ctx.ensure_object(dict)` → `ctx.obj["debug"]` の順序も正しい。click は
  グループのコールバックを実行し**終えてから**サブコマンドの `Context` を
  作るので、サブコマンド側から必ず見える
- `bool(debug) or bool(ctx.obj.get("debug", False))` の OR は、決まった
  「グループ側の `--debug` を引き継ぐ」と一致。片方だけでも DEBUG になる
- 2 回目の `loggerInit()` については 2-2 に書いたとおり実害なし

### 3-2. `click_utils.py` の型ヒント

実際の使われ方と矛盾しない。

- `click.version_option()` / `click.option()` / `click.help_option()` /
  `click.pass_context` はいずれも `Callable[[FC], FC]`（`FC` は
  `Command | Callable[..., Any]` 束縛の TypeVar）なので、
  `Decorator = Callable[[Func], Func]` に代入でき、`FC` は
  `Callable[..., Any]` に束縛される。`_decorator` の戻り値も `Func` と合う
- `click_common_opts(...) -> Decorator` を通すと、静的には関数の
  シグネチャが `Callable[..., Any]` に潰れる。ただし各コマンドは
  その上に `@click.group(...)` / `@cli.command(...)` が乗って `Group` /
  `Command` になるので、呼び出し側（`cli(prog_name=...)`）で困らない。
  TypeVar を使えばシグネチャは保てるが、click のデコレータ自体が
  引数の対応を検査しないので、**実際に防げるミスは増えない**。
  tmr 版との差を型ヒントだけに保つ方針からしても、今の形でよい
- なお `click_common_opts` は必ず `click.pass_context` を付けるので、
  今後このデコレータを付けるコマンドは第 1 引数に `ctx` が要る。忘れると
  click は全パラメータをキーワードで渡すため
  `got multiple values for argument '<第1引数名>'` の TypeError で
  **はっきり落ちる**（黙って壊れない）。注意書きは要らないと判断した

### 3-3. 全コマンドに `version_option` が付いた副作用

- **`--help` の重複は起きない。** click 8.4 の
  `Command.get_help_option_names()` は、既存パラメータが持つ名前を
  `ctx.help_option_names` から差し引く。`click_common_opts` の
  `help_option("--help", "-h")` が `--help` を持つので自動追加は
  行われず、`get_params()` の重複警告
  （`The parameter --help is used more than once.`）も出ない。
  `CONTEXT_SETTINGS`（`help_option_names`）を消した影響も無い
- **オプションが処理される順序は問題なし。** `iter_params_for_processing()` が eager
  （`--version` / `--help`）を先に処理するので、
  `ytsched x-data1 abc --version` のように他の引数が不正でも
  バージョンを出して終了する。`--datadir` の `click.Path(exists=True)` の
  検証よりも先に出る
- **`%(prog)s` は常にルートの `ytsched`。** `version_option` の callback が
  `ctx.find_root().info_name` を使うため、`ytsched webapp -V` でも
  `ytsched <ver>` になる（`ytsched webapp <ver>` にはならない）
- **短縮オプションの衝突なし。** 既存は `-p` `-r` `-w` `-u` `-l` `-d` で、
  新しく入る `-V` `-v` `-h` とぶつからない
- ヘルプの並びも意図どおり。`click_common_opts` を最下段に置いているので、
  共通オプションはコマンド固有オプションの**後ろ**に並ぶ

### 3-4. `WebServer` から `version` を消したことの追随

追随漏れは無かった。

- `WebServer(...)` の呼び出しは `src/ytsched/__main__.py:212` と
  `tests/test_webapp.py`（4 箇所）だけで、テストはすべてキーワード引数
  （`datadir=` / `debug=`）。`version` を位置引数で渡している箇所は無い
- `tests/helpers.py:48` の `version="0.0.0"` は
  `tornado.web.Application(...)` の設定で、`WebServer` の引数ではない。
  `test_handler.py:38` の `handler._version` も同じ経路。**消してはいけない**
- `webapp.py` の `PROG_NAME` / `AUTHOR` / `VERSION` の import は
  テンプレート用に残っており、`import sys` の削除も正しい
  （`sys` は他に使われていない）
- `webroot/templates/` は `version` を Application の設定から受け取るので
  影響なし
- 挙動としては、`os.makedirs(self._datadir)` の**前**にバージョンを出して
  終了する点が旧実装と同じで、副作用の順序も変わっていない。むしろ
  コンストラクタから `sys.exit()` が消えたぶん、`WebServer` を
  テストから作るときの危険が減っている

### 3-5. 文書

`README.md` / `docs/Developer.md` / `tests/README.md` に、`--version` や
共通オプションを説明している箇所は無く（grep 済み）、書き直しは要らない。
`docs/data-format.md` の `ytsched migrate` のオプション表は
`--debug` / `-d` を挙げているが、これは今も正しい（`--help` を載せて
いなかったのと同じ扱いで、`--version` を足す必要は無いと判断した）。
唯一の追随漏れが 1-1。

---

## 4. 好みの範囲・範囲外（確信度は下がる）

- **`_is_debug()` に型ヒントが無い**（`__main__.py:49`）。
  `ctx: click.Context, debug: bool) -> bool` と書けるもの。ただし
  `__main__.py` の関数はどれも型ヒントが無く、`basedpyright` は
  `standard`、mypy も `disallow_untyped_defs` を入れていないので
  **今の設定では通る**。ファイル全体を揃えるなら別項目（実装者の報告にも
  「範囲外」とある）
- `_is_debug()` の docstring にある「`cli` を経由しない呼び出し」は、
  現在このリポジトリには存在しない経路（entry point は
  `ytsched.__main__:cli` だけ）。防御としては妥当だが、
  「将来 `CliRunner` でサブコマンドを直接叩く場合に備えて」と書いたほうが
  誤解が無い。好みの範囲
- `cli` の `help="""sample package"""`（`__main__.py:64`）と、
  モジュール docstring の `main for musicbox package`（6 行目）が
  雛形の名残のまま。`ytsched --help` の先頭に出るので目に付くが、
  **TODO-036 の範囲外**。別項目にする価値はある
- `debug = _is_debug(ctx, debug)` は引数を上書きしている。読み違えの
  もとになるので `debug = _is_debug(ctx, debug)` ではなく別名にする手も
  あるが、3 箇所とも直後に使い切っており実害は無い。好みの範囲
