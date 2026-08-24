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

## コードを触る前に読むこと

構成・データモデル・Web の構成・開発コマンドは、この文書ではなく
以下に分けてある。**リンク先は自動では読まれないので、コードを触る前に
必ず開くこと。**

- ソースコードの構成、クラス構造（`SchedDataEnt` / `SchedDataFile` /
  `SchedData`、`HandlerBase` / `MainHandler` / `EditHandler` の関係、
  フィルタ・検索文字列の扱い、`base.html` の autoescape）は
  `src/README.md`
- 技術スタック、開発環境の用意、`mise` のタスクと個別コマンド、
  テストの走らせ方は `docs/Developer.md`
- 各テストファイルが何を見ているか、`helpers.py` の役割、
  ゴールデンマスターテストの位置づけは `tests/README.md`
- データの保存形式（JSON Lines、壊れた行の扱いなど）は
  `docs/data-format.md`

## ログ

`mylog.py` のラッパを使う。標準の `logging` は使わない
（TODO-007 で loguru へ移行済み）。クラス本体に
`__log = getLogger(__qualname__)` を 1 つ置く。サンプルは
`docs/Developer.md` を参照。

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

### トークン消費量の記録

`~/.claude/CLAUDE.md` の `消費:` 行に書く数字は、`tools/token-usage.py`
で集計する（TODO-035）。Claude Code の transcript
（`~/.claude/projects/-home-ytani-work-ytsched/`）を読み、親セッションと
サブエージェントの両方を合わせて数える。

```
mise run tokens -- TODO-034
mise run tokens -- TODO-034 --since '2026-08-23 14:00:00'
mise run tokens -- --list
```

範囲は git のコミット時刻で切る。始点は `docs(todo): … を TODO-NNN と
して立てる`、終点は `feat/fix(...): …（TODO-NNN）`。**どちらもコミット
メッセージの 1 行目だけを見る**（本文まで見ると、別の項目に触れている
コミットを拾ってしまう）。

- **立ててから着手まで空いた項目は、`--since` で始点を指定する。**
  そうしないと、間に挟まった他の項目の作業まで数に入る。TODO-029 は
  `--since` の有無で cache_creation が 1,042,774 と 301,888 に分かれた
- 出力の 2 行目（`（参考: cache_read …）`）は archives に貼らない。
  画面で見るためのもの
- **概算料金の単価は `tools/token-usage.py` の `PRICING` に持たせてある**
  （TODO-044）。**Sonnet 5 の $2/$10 は 2026-08-31 までの導入価格**なので、
  そのあとは $3/$15 に書き換える
- **過去の項目は遡れない。** transcript が 2026-08-22 以降しか残っていない

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
