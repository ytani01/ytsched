# TODO-023. mise.toml の見直し

見込み: main = Opus 5 / effort high、担当 = verifier + wording
実施: main = Opus 5 / effort high、担当 = verifier + wording

分担の理由と各担当の報告は
[`archives/agents/TODO-023/`](../agents/TODO-023/README.md) にある。

## きっかけ

`mise.toml` は TODO-004 で `tmr` の構成をそのまま持ってきたもので、
ytsched では使いにくいところが 3 つあった。

1. **`upgradeapt` が `sudo apt` を叩く。** 今の環境は Arch 系で apt が
   無く、これに依存する `upgrademise` → `upgradeuv` ごと動かない
2. **`lint` が `upgradeproject` に依存している。** `mise run test` を
   叩くたびに `rm -f uv.lock` → `uv sync` → `uv pip install -U` が走り、
   テストが壊れたときに変更のせいか依存が上がったせいかが分からなくなる
   （TODO-022 で、担当に `mise run lint` / `mise run test` を走らせない
   運用にしたのはこのため）
3. **アプリを動かすタスクが無い。** `webapp` の起動も `migrate` も、
   README のコマンドを手で写していた

## やったこと

### OS・mise・uv 自体を更新するタスクを消した

`upgradeapt` / `upgrademise` / `upgradeuv` の 3 つ。OS や mise、uv 自体の
更新は、このプロジェクトの `mise.toml` の仕事ではない。

同じ名前のタスクが `~/mise.toml` にもあるので、`mise tasks` の
一覧には今も出る。プロジェクトの `mise.toml` から来ていないことは、
`mise tasks --json` の `source` で確かめた。

### `lint` の `upgradeproject` への依存を切った

`upgradeproject` 自体は中身を変えずに残し、**どこからも依存されない**
タスクにした。依存を上げ直したいときに `mise run upgradeproject`
（`uppj`）と明示的に叩く。

これで `mise run lint` / `test` / `build` を叩いても依存が上がらなく
なったので、**担当にも叩かせてよくなった**（`CLAUDE.md` の
「担当への共通の前提」を書き直した）。走らせないのは
`mise run upgradeproject` だけ。

### `fmt` と `typecheck` を分け、`lint` はその 2 つを呼ぶだけにした

整形だけ、型チェックだけを叩けるようにするため。

`typecheck` には `wait_for = ["fmt"]` を付けた。`depends` ではないので、
**`mise run typecheck` だけを叩いたときに `fmt` は走らない**。両方走る
とき（`mise run lint`）だけ、整形が終わってから型を見る順になる。

`lint` は `depends` だけで `run` を持たない。

### `webapp` と `migrate` のタスクを足した

どちらも引数なしで叩ける（`webapp` は `~/ytsched/data`・port 10085）。
変えるときは `mise run webapp -- --port 10086` のように `--` のあとへ
書く（mise が引数を行の末尾へ足す）。

### 各タスク末尾の `uv run ytsched --help` を減らした

`lint` / `test` / `build` の末尾に付いていたものを消し、
`upgradeproject` にだけ残した。依存を入れ直したあとに、コマンドが
起動するかを見るためのもの。整形やテストのたびに走らせる意味は無い。

## テスト

`mise.toml` にはコードが無いので pytest は無い。verifier に、
タスクを実際に走らせて確かめさせた
（[verifier-report.md](../agents/TODO-023/verifier-report.md)）。

- `fmt` / `typecheck` / `lint` / `test` / `build` が単独で成功する
  （`test` は 330 passed、`build` は sdist と wheel を作った）
- `mise run lint` の出力で `[fmt]` が先、`[typecheck]` があと
- `mise run typecheck` 単独では `fmt` が走らない
- `mise run test` の前後で `uv.lock` の mtime が変わらない
  （`upgradeproject` が走っていない）
- `mise run webapp -- --datadir <一時ディレクトリ> --port 18085` で
  起動し、`/ytsched/` が 200 を返す（テンプレートも展開済み）
- `mise run migrate -- --datadir <一時ディレクトリ> --dry-run` で、
  両方の引数が `ytsched migrate` に渡る

不具合は見つからなかった。

reviewer は入れていない。アプリの分岐も条件式も変わらないため。
