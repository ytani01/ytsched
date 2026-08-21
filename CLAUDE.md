# CLAUDE.md（ytsched）

`~/.claude/CLAUDE.md`（ユーザー全体の指示）が前提。ここには書かない。

## これは何か

個人用のスケジュール帳（Web アプリ）。2021 年に Perl CGI 相当で作った
ものを、Python 3.14 / uv / pytest の環境へ移行したもの。単一ユーザ専用で、
認証はリバースプロキシに任せる前提（`README.md` 参照）。

データディレクトリ（既定 `~/ytsched/data`）は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にあり、形式に
ついての決まりはそちらが置き場所（形式を変えたらあの文書も書き直す）。
既存データは `ytsched migrate` で一度に変換する。

## 構成

```
src/ytsched/
  ytsched.py       # データモデル: SchedDataEnt / SchedDataFile / SchedData
  handler.py       # HandlerBase（tornado.web.RequestHandler の共通部分、Conf.cgi の読み書き）
  main_handler.py  # MainHandler（一覧表示・追加/修正/削除の実行）
  edit_handler.py  # EditHandler（編集画面）
  webapp.py        # WebServer（tornado.web.Application の組み立て、CLI から呼ばれる）
  mylog.py         # loguru ラッパ（TODO-007）
  __main__.py      # click による CLI（`ytsched` コマンド）
  webroot/
    templates/      # tornado のテンプレート（base/main/edit/sde.html）
    static/         # CSS・JS・favicon
tests/
  helpers.py        # webapp.WebServer と同じ Application をテスト用に組み立てる
  test_ytsched.py   # データモデルのテスト
  test_handler.py, test_web.py, test_webapp.py, test_mylog.py
archives/
  todo/    # 決着した TODO 項目（1 項目 1 ファイル）
  agents/  # サブエージェントに分担させたときの依頼・報告
```

CLI には `webapp`（Web サーバ、本来の入口）のほかに `x_data1` という
デバッグ用のサブコマンドが残っている（指定した 1 日分のデータを
標準出力へダンプするだけで、`webapp` の動作には関係ない）。

## データモデルの勘所

- **`SchedDataEnt`** が 1 件の予定・ToDo。`sde_id`（UUID）、`date`、
  `time_start`/`time_end`、`type`、`title`、`place`、`detail` を持つ。
  - `type` の先頭が `"□"` なら ToDo（`is_todo()`）。ToDo は `date` を
    「締切」として扱う
  - `title` の先頭文字列で「重要」（`is_important()`）「取り消し」
    （`is_canceled()`）を判定する。先頭に決まった文字列を置くだけで、
    フィールドは増やさない設計
  - `detail` は常に素のテキスト（改行・タブもそのまま持てる）。
    保存・読み込みで文字列を変換しない。**画面の改行表示は CSS の
    `white-space: pre-wrap` が担っている**（テンプレート側でタグを
    差し込んでいるわけではない）
  - 「重要」「取り消し」の判定、`get_sortkey()`、`search_str()` は、
    モジュール関数 `normalize()` を通した文字列で照合する。全角括弧を
    半角にして小文字にするだけで、**保存する文字列そのものは変えない**。
    詳しくは `docs/data-format.md`

- **`SchedDataFile`** が 1 ファイル（1 日分、または ToDo 全体）の
  読み書きを担う。形式は JSON Lines（1 行 1 件）、文字コードは utf-8
  のみ。
  - パスは `date2path()` で決まる。日付ありなら
    `{topdir}/{年}/{月}/{日}.jsonl`、`date=None` なら ToDo として
    `{topdir}/ToDo.jsonl`
  - 読み込みは**行ごとに**デコード・パースする（ファイル単位ではない）。
    読めない行（空行、utf-8 で読めない、JSON として読めない、
    オブジェクトでない、`date` が無い／読めない）はその行だけ飛ばして
    警告を出し、ファイル全体は捨てない
  - **飛ばした行のうち、空行を除く 4 種類は生のバイト列のまま覚えて
    おき、次の `save()` でファイルの末尾へ元のバイトのまま書き戻す**
    （予定の行が先、飛ばした行があと）。保存をくり返しても壊れた行は
    失われず、読み直すたびにまた飛ばされて警告も出続ける。**空行だけは
    書き戻さない**（失うデータが無いため、保存すると消える）。詳しくは
    `docs/data-format.md`
  - 保存は毎回全件を書き直す。既存ファイルが空でなければ `.bak` へ
    退避してから上書きする（空ファイルは退避しない＝`.bak` にしか
    残っていないデータを空で潰さないため）

- **`SchedData`** が `SchedDataFile` を日付ごとにキャッシュする
  （`collections.OrderedDict`、LRU 的に古いものから捨てる）。
  `MainHandler` / `EditHandler` はここを経由してデータへアクセスする
  （`SchedDataFile` を直接は触らない）

- 設定（`Conf.cgi`）はデータディレクトリの直下にあり、`HandlerBase` が
  リクエストのたびに読み書きする。人が手で編集するファイルではない
  （TODO-011 で TOML 化を検討し、見送っている。理由は
  `archives/todo/TODO-011. 設定ファイル Conf.cgi の形式（対応しない）.md`）

## Web の構成

- `WebServer`（`webapp.py`）が `tornado.web.Application` を組み立てる。
  URL は `/ytsched`（`WebServer.URL_PREFIX`）配下
- `MainHandler` が一覧表示と、追加・修正・削除の実行（`cmd=add/fix/update/del`）
  を兼ねる。`GET`/`POST` とも同じ `get()` を呼ぶ（`post()` は `self.get()`
  に委譲するだけ）
- フィルタ文字列・検索文字列は、利用者の入力を正規表現として扱う
  （利用者本人しか使わない前提）。`get()` の中で 1 回だけコンパイルし、
  **不正ならその条件を無視して全件を出す**（TODO-012）。入力欄の文字列と
  `Conf.cgi` への保存は不正でもそのまま残し、マッチに使うかどうかだけを
  分けている。検索モードかどうかは「文字列が空でないか」ではなく
  「コンパイルできたか」で判定する（`search_mode`）
- `base.html` は `{% autoescape None %}` のまま（エスケープを切っている）。
  単一ユーザ・自分の入力しか自分に見えないため実害が無いと判断し、
  現状維持と決めている（TODO-012。詳細は
  `archives/todo/TODO-012. 不正な正規表現を入れられたときの扱い.md`）

## コマンド

`mise.toml` にタスクがある（`lint` → `test` → `build` の順に依存する。
`lint` は `fmt` と `typecheck` を呼ぶだけ）。

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
```

`upgradeproject`（`uppj`）は依存を上げ直すタスクで、**どこからも依存されて
いない**。`rm -f uv.lock` → `uv sync` → `uv pip install -U` が走るので、
上げ直したいときに明示的に叩く（TODO-023）。

個別に実行する場合:

```sh
uv run pytest tests
uv run ruff format --line-length 78 src tests
uv run ruff check --fix --extend-select I src tests
uv run basedpyright src tests
uv run mypy src tests
```

アプリの起動:

```sh
uv run ytsched webapp --datadir ~/ytsched/data --port 10085
```

旧形式（タブ区切り `.cgi`）から JSON Lines への移行（`ytsched migrate`、
オプションは `docs/data-format.md` 参照）:

```sh
uv run ytsched migrate --datadir ~/ytsched/data
```

## ログ

`mylog.py` のラッパを使う。クラス本体に
`__log = getLogger(__qualname__)` を 1 つ置く（`mylog.py` の
モジュール docstring にサンプルがある）。標準の `logging` は使わない
（TODO-007 で loguru へ移行済み）。

## サブエージェントの分担

基準そのものは `~/.claude/CLAUDE.md` にある。ここには、TODO-001〜016 を
見直して基準を決めたときの材料を残す（TODO-017）。

- **reviewer を入れたのは TODO-003・005・006 の 3 件だけで、3 件とも
  実質的な指摘を出した。** TODO-005 の「`save()` が空でも書くように
  なり、`.bak` が空で上書きされる経路が増えた」は、テストが通ることを
  見ても出てこない種類の指摘。TODO-006 の指摘 1-1 / 2-2 は、そのまま
  TODO-016 になった
- 一方、TODO-007 以降は一度も入れていない。TODO-012（`search_mode` の
  判定条件そのものを変えた）は入れる余地があった。**挙動や分岐が
  変わる項目には入れる**と決めたのは、この差から
- **verifier は 12 件すべてで立てたが、発見がゼロだった項目がある。**
  TODO-014 は定義ファイル 4 つを grep して形式を見るだけだった。逆に
  TODO-009 の「README の手順を実際に再現する」（`uv tool uninstall` →
  再インストール → curl）は明らかに効いた。**書式の確認だけなら main、
  試せる手順があるなら分ける**と決めたのは、この差から

### 文書の確認（wording）と hook

**`.md` が入るコミットでは、`wording` を立てて前例の無い語を挙げさせる**
（TODO-025・TODO-026）。コードの確認を実装者と分けるのと同じ理由で、
**書いた本人は自分の造語に気づけない**（TODO-021 で `characterization
test` を「足場」と呼び、2 度指摘された）。

- **対象は、そのコミットに入る `.md` 全部。** 依頼書・archives・
  `CLAUDE.md`・README に加えて、**担当の報告ファイルも含める**
  （「足場」が入っていたのが報告ファイルだった）
- **前例なし ＝ 造語ではない。** 一般に通用する専門用語でも、この
  リポジトリでは初出になる。`wording` は候補を十数語に絞って見立てを
  添えるところまでで、**決めるのは main**
- `.claude/hooks/check-md-commit.sh` が `git commit` を捕まえて、`.md` が
  入っていれば促す。**判断はしないし、止めない。** 立て忘れを思い出す
  ためのもので、これがあるから `wording` が要らなくなるわけではない

hook を効かせるには `.claude/settings.json` が読まれている必要がある。
**Claude Code は起動時にしか設定を読まないので、置いたり直したら再起動が
要る**（再起動するのは利用者）。定義ファイルと同じ。

### 担当への共通の前提

**プロジェクトの前提を `.claude/agents/*.md` へ書き写さない。**
サブエージェントには、この `CLAUDE.md` と `~/.claude/CLAUDE.md` の両方が
そのまま届いている（TODO-022 で実測）。定義ファイルに書くのは、
**その担当の役割と、その担当だけに要る注意**にとどめる。

CLAUDE.md に書きようが無くて、どの担当にも要るものだけをここに置く。

- **アプリの起動を確かめるときは、`--datadir` に必ず一時ディレクトリを
  指定する。** `~/ytsched/data` の実データを汚さないため
- **`mise run upgradeproject` は、担当には走らせない。**
  `rm -f uv.lock` → `uv sync` → `uv pip install -U` が走り、呼ぶたびに
  依存を上げ直す。テストが壊れたときに、変更のせいか依存が上がったせいかが
  分からなくなる（TODO-022）。**`mise run fmt` / `typecheck` / `lint` /
  `test` / `build` は叩かせてよい。** `lint` の `upgradeproject` への
  依存は切ってあるので、依存は上がらない（TODO-023）。
  `uv run ruff format` / `ruff check` / `basedpyright` / `mypy` /
  `pytest` を個別に叩かせてもよい
