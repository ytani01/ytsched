# 依頼: TODO-030 ドキュメントの整備（writer）

`TODO.md` の TODO-030 の節を読んでから始めること。役割分担と「決めたこと」
「気をつけること」はそちらにある。

## やること

### 1. `src/README.md` を新規に作る

ソースコードの構成とクラス構造の、全体的な説明。

- `src/ytsched/` の各モジュールが何を担当するか
- `SchedDataEnt` / `SchedDataFile` / `SchedData` の関係と、
  `MainHandler` / `EditHandler` / `HandlerBase` の関係
- Web の構成（URL、`MainHandler` が一覧と追加・修正・削除を兼ねること、
  フィルタ・検索文字列の扱い、`base.html` の autoescape）
- **個別の docstring を読めば分かる細部は書かない。**
  引数の一覧やメソッドごとの説明は要らない
- データ形式そのものは `docs/data-format.md` へリンクして委ねる

材料は今の `CLAUDE.md` の「構成」「データモデルの勘所」「Web の構成」の
3 節にある。ただし丸写しにせず、**人間の開発者が初めて読む順序**に組み直す
こと（`CLAUDE.md` は Claude 向けの箇条書きで、読み物になっていない）。

### 2. `docs/Developer.md` を新規に作る

開発者向け。技術スタックと開発ツール。

- 使っているもの（Python 3.14 / uv / tornado / click / loguru / pytest /
  ruff / basedpyright / mypy / mise）と、それぞれ何のためか
- 開発環境の用意（クローンから `uv sync` まで）
- `mise` のタスク（`fmt` / `typecheck` / `lint` / `test` / `build` と
  依存関係、`webapp` / `migrate` の引数の渡し方、`upgradeproject` が
  どこからも依存されていないこと）
- 個別コマンドで実行する場合の書き方
- テストの構成（`tests/` の各ファイルが何を見ているか、`helpers.py` の役割）
- ログの書き方（`mylog.py` のラッパ、クラス本体に
  `__log = getLogger(__qualname__)` を 1 つ置く。標準の `logging` は使わない）
- `README.md` の末尾にある「memo」節（JavaScript の `Date` の罠と
  `javascript-scroll.svg`）をここへ移す。**画像は `docs/` にあるので、
  この文書からの相対パスは `javascript-scroll.svg`**（`docs/` を付けない）
- コードの構造は `src/README.md` へリンクして委ねる

材料は今の `CLAUDE.md` の「コマンド」「ログ」節と `README.md` の「memo」節、
`mise.toml`、`pyproject.toml`。

### 2-b. `tests/README.md` を新規に作る（あとから足した）

テストの構成。`src/README.md` がソースに対して担うのと同じ役割を、
`tests/` に対して担う。

- `tests/` の各ファイルが何を見ているか
- `helpers.py` の役割（`webapp.WebServer` と同じ Application を組み立てる）
- ゴールデンマスターテスト（TODO-021 で足したもの）の位置づけと、
  挙動を変えたときに書き直してよいこと
- fixture やテストデータの置き場所
- **走らせ方は書かない。** `mise run test` や `pytest` の叩き方は
  `docs/Developer.md` にあるので、そちらへリンクする

これに伴い、`docs/Developer.md` の「テストの構成」は**走らせ方だけ**にして、
構成は `tests/README.md` へリンクで委ねること。

### 3. `CLAUDE.md` の重複部分をリンクに置き換える

「構成」「データモデルの勘所」「Web の構成」「コマンド」の 4 節の本文を消し、
`src/README.md` と `docs/Developer.md` を指す短い節に差し替える。
**「コードを触る前に読むこと」と明記する**（リンク先は自動では読まれない）。

「これは何か」「ログ」「サブエージェントの分担」は `CLAUDE.md` にしか無い
内容なので残す（「ログ」は書き方の決まりなので、詳細を `docs/Developer.md`
に置いたうえで、守るべき一行だけ残すか、リンクにするかは判断してよい）。

### 4. `README.md` から開発者向けの記述を移す

利用者用にする。「memo」節を `docs/Developer.md` へ移し、
「開発者向けは docs/Developer.md」というリンクを足す。
インストール・systemd の手順は利用者向けなので残す。

### 5. 相互リンクを張る

6 つの文書（`README.md`・`docs/Developer.md`・`docs/data-format.md`・
`src/README.md`・`tests/README.md`・`CLAUDE.md`）が、関係するもの同士から
辿れるようにする。
`docs/data-format.md` は**中身を変えず、リンクだけ足す**。

## 守ること

- **リンクは相対パスで書き、実際に辿れることを自分で確かめる**
  （文書ごとに階層が違う。`docs/` から `src/README.md` は `../src/README.md`）
- 既存の文書の文体に合わせる。`README.md` は「です・ます」に近い調子、
  `CLAUDE.md` と `docs/data-format.md` は「である」調の箇条書き
- **書いた内容が今のコードと合っているかを、コードを読んで確かめる。**
  `CLAUDE.md` からの書き写しで済ませない。`migrate.py` は `CLAUDE.md` の
  「構成」の一覧から漏れている（`src/README.md` には入れること）
- コマンド例は、書く前に実際に叩いて出力を確かめる。
  アプリを起動して確かめるときは `--datadir` に一時ディレクトリを指定する

## 報告

`archives/agents/TODO-030/writer-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
