# TODO-029 verifier の報告

## 1. `mise run test`

○ 通った。**402 件、全部 pass**（`mise run test` の出力どおり）。

```
$ mise run test
[fmt] $ echo "# ruff format"
21 files left unchanged
# ruff check
All checks passed!
[typecheck] $ echo "# basedpyright"
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 18 source files
[test] $ uv run pytest tests
============================= test session starts ==============================
collected 402 items
...
============================= 402 passed in 2.65s ==============================
```

## 2. `mise run lint` / `mise run typecheck`

○ 通った（上の `mise run test` の中で `fmt` → `typecheck` → `test` の順に
走るので、実質同じ実行で両方確認できた）。`ruff format` は 21 ファイル
とも変更なし、`ruff check` は指摘無し、`basedpyright` は 0 件、`mypy` は
18 ファイルとも issue なし。

## 3. implementer 報告の「確かめたこと」を自分でも再現

**すべて一時ディレクトリで実施**
（`/tmp/claude-649/.../scratchpad/ytsched-verify/data`）。
`~/ytsched/data` の実データには触れていない。

### 3-1. `\r` の除去（移行）

`.cgi` を CRLF で用意して `uv run ytsched migrate --datadir <一時dir>` を
実行。

```
$ printf '1627783337-9999999\t2021/03/01\t10:00-11:00\t予定\t会議\t会議室\t議題<br />・進捗\r\n' > .../2021/03/01.cgi
$ uv run ytsched migrate --datadir <一時dir>
変換した行      : 1
```

生成された `.jsonl`:

```json
{"sde_id": "1627783337-9999999", "date": "2021-03-01", ...,
 "detail": "議題\n・進捗"}
```

`grep -c $'\r'` で `\r` が 0 件であることを確認。○ 報告どおり
（1 回目は列数を実データと合わせずに試して `date=''` のエラーで空振り
したが、7 列に合わせて作り直したら報告どおりになった。これは自分の
テストデータの作り方の問題で、実装の不具合ではない）。

### 3-2. edit 画面の `orig_date`

一時ディレクトリでサーバを起動（`uv run ytsched webapp --datadir <一時dir>
--port 18765`）し、`2021/03/01.jsonl` に `date=2021-03-05` の行
（`sde_id=id-a`）を置いて確認。

| 操作 | 結果 |
| --- | --- |
| `GET /ytsched/edit?date=2021-03-01&sde_id=id-a` | `orig_date` の隠しフィールドは `2021-03-01`（ファイル） |
| `POST cmd=fix`（`orig_date=2021-03-01`） | `2021/03/01.jsonl` から `id-a` が消え、`2021/03/05.jsonl` に 1 件だけ現れる（重複なし） |

○ 報告どおり再現できた。

### 3-3. 検索・フィルタの `normalize()`

`会議（重要）の件`（`id-a`, 2021-03-05）と `歯医者`（`id-b`, 2021-03-01）
を置き、`search_str=（重要）` で POST（`cur_day=2021-03-10` を指定、検索
モードは指定日から**過去方向**にしか探さない実装のため、対象日より
後の `cur_day` を指定する必要があった。これは仕様どおりで、実装の
不具合ではない）。

- 結果ページに「会議（重要）の件」が 1 件だけ現れ、「歯医者」は現れない
- `Conf.cgi` は `SearchStr\t(重要)`（全角括弧が半角へ正規化されて保存）

○ 報告どおり。

### ログ

サーバの `stderr`（`server.log`）に例外・トレースバックは無し。出た
警告は 1 件のみで、これは TODO-029 の「読み込みの方針は変えない」で
維持すると決めた既知の挙動:

```
WARNING migrate.py / ytsched.py:558 load_line()> .../2021/03/01.jsonl:1:
date=2021-03-05 != 2021-03-01 .. use the date in the line
```

### 後始末

一時ディレクトリで起動したサーバは `pgrep` で PID を確認してから
`kill` し、停止を確認済み。`~/ytsched/data` には一切触れていない。

## 見つかったこと

実装・テストとも問題は見つからなかった。

## 判断が要る点

無し。`.md` の造語チェック（`wording`）は今回の依頼の範囲外だったので
実施していない（TODO.md のメモに「`wording` の確認」がまだ残っている
ので、必要ならそちらを別途走らせてほしい）。
