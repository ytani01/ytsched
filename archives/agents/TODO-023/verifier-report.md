# verifier 報告（TODO-023）

作業ディレクトリ: `/home/ytani/work/ytsched`

## 1. タスク一覧と source

```
$ mise tasks
build           build
fmt             format (ruff)
installmise     install mise
installuv       install uv by mise
lint            linting (fmt, typecheck)
migrate         migrate old data (.cgi) to JSON Lines
test            test
typecheck       type check (basedpyright, mypy)
upgradeapt      upgrade apt packages
upgrademise     upgrade mise
upgradeproject  upgrade in this project
upgradeuv       upgrade uv
webapp          run web server
```

`mise tasks --json` の `source` で確認（抜粋）:

```
upgradeapt      | /home/ytani/mise.toml
upgrademise     | /home/ytani/mise.toml
upgradeuv       | /home/ytani/mise.toml
upgradeproject  | /home/ytani/work/ytsched/mise.toml
fmt             | /home/ytani/work/ytsched/mise.toml
typecheck       | /home/ytani/work/ytsched/mise.toml
lint            | /home/ytani/work/ytsched/mise.toml
test            | /home/ytani/work/ytsched/mise.toml
build           | /home/ytani/work/ytsched/mise.toml
webapp          | /home/ytani/work/ytsched/mise.toml
migrate         | /home/ytani/work/ytsched/mise.toml
```

○ 依頼どおり `upgradeapt` / `upgrademise` / `upgradeuv` はホーム側
（`/home/ytani/mise.toml`）から来ていて、プロジェクトの `mise.toml`
からは消えている。一覧には出る。

## 2. 各タスク単独での成功

- `mise run fmt` → ○（`19 files left unchanged` / `All checks passed!`）
- `mise run typecheck` → ○（`0 errors, 0 warnings, 0 notes` /
  `Success: no issues found in 18 source files`）
- `mise run lint` → ○（fmt → typecheck の順、両方成功）
- `mise run test` → ○（`330 passed in 1.24s`）
- `mise run build` → ○（`lint` → `test` → `build` と連鎖し、
  `dist/ytsched-0.1.1.dev21+gecbd3b519.d20260821.tar.gz` と
  `.whl` を作成）

## 3. lint での fmt → typecheck の順

`mise run lint` の出力:

```
[fmt] $ echo "# ruff format"
# ruff format
19 files left unchanged
# ruff check
All checks passed!
[typecheck] $ echo "# basedpyright"
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 18 source files
Finished in 1.60s
```

○ `[fmt]` が先、`[typecheck]` があとに出た。順が守られている。

## 4. typecheck 単独で fmt が走らないこと

`mise run typecheck` の出力（上記 2 参照）には `[fmt]` の行が無く、
`ruff format` / `ruff check` の出力も出ない。basedpyright / mypy の
出力だけ。○ fmt は走っていない。

## 5. upgradeproject がどこからも依存されていないこと

```
$ stat -c '%Y %n' uv.lock
1787251979 uv.lock
$ mise run test   # (fmt/typecheck/lint も連鎖して走る)
... 330 passed in 1.24s ...
$ stat -c '%Y %n' uv.lock
1787251979 uv.lock
```

○ `mise run test` の前後で `uv.lock` の mtime は同一
（`1787251979` のまま）。`upgradeproject` は走っていない。
`mise run upgradeproject` 自体は依頼どおり実行していない。

## 6. webapp タスクの起動確認

```
$ mise run webapp -- --datadir <一時ディレクトリ> --port 18085
```

- `curl -s -o resp.html -w "%{http_code}\n" http://127.0.0.1:18085/ytsched/`
  → **200**
- `resp.html` を grep したところ `{{` `{%` は残っていない（テンプレート展開済み）
- サーバのログ（webapp.log）:
  ```
  [webapp] $ uv run ytsched webapp --datadir /tmp/.../ytsched-verify-data --port 18085
  08/21 16:24:28 ℹ️ INFO webapp.py:125 main()> start server: run forever ..
  ```
  例外・トレースバックは無し
- 使った一時ディレクトリ:
  `/tmp/claude-649/-home-ytani-work-ytsched/db015107-d10e-45c8-bd80-33e5deca4ef5/scratchpad/ytsched-verify-data`
  （`~/ytsched/data` には触れていない）
- プロセスの停止: `ps -eo pid,args | grep -i "ytsched webapp" | grep -v grep`
  で PID（269216, 269220）を確認してから `kill 269216 269220`。
  停止後に再度 `ps` で確認し、プロセスが残っていないことを確認した

## 7. migrate タスクへの引数の受け渡し

```
$ mise run migrate -- --datadir <一時ディレクトリ> --dry-run
[migrate] $ uv run ytsched migrate --datadir /tmp/.../ytsched-verify-data …
08/21 16:24:45 ⚠️ WARNING migrate.py:324 main()> /tmp/.../ytsched-verify-data: no target file .. check --datadir
08/21 16:24:45 ℹ️ INFO __main__.py:133 migrate()> end
===== dry run: 書き出していません =====
変換したファイル: 0
```

○ `--datadir` と `--dry-run` の両方が `ytsched migrate` に渡っている
（指定した一時ディレクトリを見に行き、dry-run の出力が出た）。

## まとめ

依頼の 1〜7 すべて確認でき、不具合は見つからなかった。
`mise run upgradeproject` は依頼どおり実行していない。
