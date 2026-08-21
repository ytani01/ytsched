# verifier への依頼（TODO-023）

`mise.toml` を書き直した。**独立に走らせて確かめてほしい。**
コードは直さないこと。見つけたことは報告する。

## 何を変えたか

- `upgradeapt` / `upgrademise` / `upgradeuv` を消した
- `lint` から `depends = ["upgradeproject"]` を外した
- `fmt`（ruff）と `typecheck`（basedpyright・mypy）に分け、`lint` は
  その 2 つを `depends` で呼ぶだけにした。順番を守らせるために
  `typecheck` に `wait_for = ["fmt"]` を付けている
- `webapp`（alias `web`）と `migrate` のタスクを足した
- 各タスク末尾の `uv run ytsched --help` は `upgradeproject` にだけ残した

## 確かめてほしいこと

1. `mise tasks` に `fmt` / `typecheck` / `lint` / `test` / `build` /
   `webapp` / `migrate` / `upgradeproject` があること。
   `upgradeapt` / `upgrademise` / `upgradeuv` が **`~/mise.toml`（ホーム側）
   から来ている**ことを `mise tasks --json` の `source` で確かめる
   （プロジェクトからは消えているが一覧には出る）
2. `mise run fmt` / `mise run typecheck` / `mise run lint` /
   `mise run test` / `mise run build` がそれぞれ単独で成功すること
3. **`lint` で fmt → typecheck の順が守られる**こと（出力の順で見る）
4. **`typecheck` を単独で叩いたときに fmt が走らない**こと
5. **`upgradeproject` がどこからも依存されていない**こと。`mise run test`
   を叩いても `uv.lock` の mtime が変わらないことで見る
   （`uv.lock` を消させないため、mtime を控えてから叩くこと）
6. `mise run webapp -- --datadir <一時ディレクトリ> --port <空きポート>` で
   起動でき、`GET /ytsched/` が 200 を返すこと。**`--datadir` には必ず
   一時ディレクトリを指定する**（`~/ytsched/data` を汚さない）。
   確認したらプロセスを止めること
7. `mise run migrate -- --datadir <一時ディレクトリ> --dry-run` に引数が
   渡ること

## 気をつけること

- **`mise run upgradeproject` は走らせないこと。** `rm -f uv.lock` →
  `uv sync` → `uv pip install -U` が走り、依存が上がってしまう
- 6 でプロセスを止めるとき、`pgrep -f` のパターンが**自分のシェルの
  コマンド行を拾う**（main が実際に踏んだ）。`ps -eo pid,args` で
  PID を確かめてから、その PID を kill すること

## 報告

`archives/agents/TODO-023/verifier-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
