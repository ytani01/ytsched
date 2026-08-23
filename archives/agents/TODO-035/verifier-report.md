# TODO-035 verifier 報告

## 結論

集計そのものは、TODO-034・TODO-029 について**独自に書いた別スクリプトで
検算し、一致を確認した**。ただし **「始点の判定」に実バグを 1 件見つけた**
（TODO-013・TODO-022 で実際に誤った数字が出る）。lint・テストは通った。

## 1. 集計の検算（本題）

`tools/token-usage.py` を import せず、独立に
`/tmp/claude-649/.../scratchpad/check.py` を新規に書いて検算した
（中身は下記に全文あり）。

### TODO-034

範囲: 2026-08-23 14:59:19+09:00（4b68048）〜 15:13:15+09:00（fe0aba3）

| 項目 | ツール出力 | 検算結果 |
| --- | --- | --- |
| 行数（重複除去前 / 後） | lines=173, uniq=90（実装者報告） | lines=173, uniq=90 |
| 担当別 output/cache_creation | main 20,018/99,153, verifier 293/33,010, wording 971/31,750 | 完全一致 |
| モデル別 | opus 20,018/99,153, sonnet 1,264/64,760 | 完全一致 |
| 合計 | output 21,282 / cache_creation 163,913 | 完全一致 |

### TODO-029

範囲: 2026-08-21 16:00:27+09:00（ecbd3b5）〜 2026-08-23 14:58:58+09:00（c925fee）

| 項目 | ツール出力 | 検算結果 |
| --- | --- | --- |
| 行数（重複除去前 / 後） | （報告に記載なし） | lines=702, uniq=396 |
| 担当別 | main 42,506/364,399, implementer 3,543/283,305, reviewer 860/187,219, verifier 383/115,444, wording 64/92,407 | 完全一致 |
| モデル別 | opus 25,475/573,713, sonnet 21,881/469,061, `<synthetic>` 0/0（4 件） | 完全一致 |
| 合計 | output 47,356 / cache_creation 1,042,774 | 完全一致 |

検算スクリプトでは、**担当別の合計・モデル別の合計・全体合計が一致する
こと**を `assert` で機械的にも確認した（両項目とも一致、`AssertionError`
なし）。

### 重複除去の妥当性

重複ペアの生の行を実際に見た（`req_...`/`msg_...` の組が同じ）。
TODO-034 の範囲で 83 組の重複を確認したが、すべて **`usage` の中身
（`input_tokens` / `cache_creation_input_tokens` / `output_tokens` などの
数値）が完全に一致する行**だった。同じ assistant メッセージ内で複数の
tool_use ブロックが記録されるたびに、同じ `usage` が繰り返し出ている形。
別の課金対象を潰してはいない ── **除去は正しい**。

### 親と subagents の両方を数えているか

TODO-029 の担当別内訳に `main` 以外（implementer / reviewer / verifier /
wording）が出ており、`~/.claude/projects/.../*/subagents/agent-*.jsonl`
も走査していることを実データで確認した
（`iter_transcripts()` が `*/subagents/agent-*.jsonl` を glob している）。

### 担当名（`agentType`）の対応付け

現在残っている `subagents/agent-*.jsonl` はすべて対応する
`agent-*.meta.json` を持つ（15 ファイル全部を `find` で確認）。
`unknown` が実際に出るケースは無い。実装者の報告と一致。

## 2. 実際に走るか

依頼書のコマンドをすべて実行した。

```
uv run python tools/token-usage.py TODO-034   → 正常終了（上表のとおり）
uv run python tools/token-usage.py TODO-029   → 正常終了（上表のとおり）
uv run python tools/token-usage.py TODO-029 --since '2026-08-23 14:30:00'
  → 始点が --since になり探索を飛ばした（実装者報告どおり）
mise run tokens -- TODO-034                   → 正常終了、同じ数字
uv run python tools/token-usage.py --list     → 一覧が出る（下記参照）
```

異常系（すべて終了コード 1、メッセージあり）:

| 入力 | 結果 |
| --- | --- |
| 引数なし | `TODO 番号を指定してください（--help）。` |
| `abc` | `ValueError: 'abc': invalid TODO number` |
| `TODO-999` | `TODO-999: 始点のコミット（\`docs(todo): … TODO-999 …\`）が見つかりません。--since で始点を指定してください。` |
| `--since 'not-a-date'` | `ValueError: Invalid isoformat string: 'not-a-date'` |
| プロジェクト外（`/tmp`） | `FileNotFoundError: /home/ytani/.claude/projects/-tmp: no transcript .. プロジェクトのトップで実行してください` |

いずれも落ち方はまとも。

## 3. 実装者が単独で決めた判断の検証

### 判断 1（コミットメッセージの 1 行目だけを見る）

依頼書の指示どおり、過去のコミットログを実際に当たった。**1 行目だけを
見る判断自体は正しい**（本文を見ると TODO-029 の始点が TODO-034 の
コミットになってしまう、という実装者の指摘は再現した）。

### 判断 2（始点より古い終点は使わない）― 見つけた不具合

**TODO-013・TODO-022 で、始点の取り違えが起きている。**

これらは現行の「`docs(todo): … を立てる` / `feat/fix(...)（TODO-NNN）`」
という規約が定着する前の、**古い規約**（決着も `docs(todo):` プレフィックス
で、本文ではなく件名に `（TODO-NNN）` を書く）を使った項目。

```
ba8b80e docs(todo): 軽量な担当 runner の件を決着させる（TODO-022）   ← 新しい
c09b5d2 feat(agents): 軽量な担当 runner を作り…（TODO-022）
06eb949 docs(todo): 軽量な担当 runner の件を TODO-022 として立てる   ← 本来の始点
```

`find_start()`（`tools/token-usage.py:168-182`）は「`docs(todo):` で
始まり `TODO-022` を含む」コミットを、**新しい順に見て最初に当たったもの**
を返す。この 3 件はどれも `docs(todo):` で始まり `TODO-022` を含むため、
`06eb949`（本来の始点）ではなく **`ba8b80e`（決着コミット、始点より
後）を始点として誤って選ぶ**。

実際の出力:

```
$ uv run python tools/token-usage.py TODO-022
TODO-022 の範囲
  始点 2026-08-21 05:36:51  ba8b80e docs(todo): 軽量な担当 runner の件を決着させる（TODO-022）
  終点 2026-08-23 15:36:22  (まだ完了していない: 現在時刻まで)
```

始点が本来より 1 時間ほど後ろにずれるだけでなく、**本当の終点
（`c09b5d2`、始点より前になってしまう）が「始点より古い」として捨てられ、
「まだ完了していない」扱いで現在時刻まで集計してしまう**。TODO-013 も
同様（`bd873dd` を誤って始点に選び、`7e93102` を捨てて現在時刻まで
集計）。この 2 件の出力は、実際の作業量とは無関係な数字（現在時刻までの
全履歴）になっている。

`--list` でも同じ症状が出ている（`TODO-022` の始点が `2026-08-21
05:36:51`、`(未完了)` と誤表示）。

**影響範囲は限定的。** 現行の規約（`CLAUDE.md` の「コミットは 2 回に
分ける」節）に従っている項目（TODO-018 以降の大半）では、決着コミットは
`docs(todo):` プレフィックスを使わないため、この不具合は起きない。
実際に踏んだのは、規約変更前の TODO-013・TODO-022 の 2 件のみ
（`--list` の出力を全部見て確認）。それ以外の項目（TODO-034・TODO-029・
TODO-030 など）は始点・終点とも正しく取れている。

### 判断 8（`<synthetic>` モデルを落とさない）

TODO-029 の実データで確認。`<synthetic>` は 4 件、いずれも
`output=0, cache_creation=0` で、合計に影響しない。落とさない判断は
実害が無く妥当。

## 4. lint・テスト

```
$ mise run lint
[fmt] ruff format: 22 files left unchanged / ruff check: All checks passed!
[typecheck] basedpyright: 0 errors, 0 warnings, 0 notes
[typecheck] mypy: Success: no issues found in 19 source files

$ uv run pytest tests
404 passed in 2.65s
```

いずれも通った。実装者の報告（`mise run lint` 通過、`404 passed`）と一致。

## 検算スクリプトの中身と結果

`/tmp/claude-649/-home-ytani-work-ytsched/0cff0fd9-667d-48a3-b131-67233ccfa77b/scratchpad/check.py`
に置いた（本題の依頼どおり、`archives/` には置いていない。一時ディレクトリ
なのでこのセッションの外では残らない。再現したい場合は同内容を書き直す
必要がある）。要旨:

- `tools/token-usage.py` を import せず、`git log` の出力と transcript の
  `.jsonl` を独自に読む
- 重複除去は `(requestId, message.id)` の集合で行う（依頼と同じ考え方だが
  コードは別）
- 担当別・モデル別・全体合計をそれぞれ集計し、`assert` で
  「担当別の合計 == 全体」「モデル別の合計 == 全体」を機械的に確認

実行結果（抜粋、`output`/`cache_creation` のみ抜粋。全文は上の表）:

```
== TODO-034 ==
lines (before dedup): 173, unique records: 90
total: output=21,282 cache_creation=163,913 cache_read=4,671,282 messages=90
OK: agent/model sums match total

== TODO-029 ==
lines (before dedup): 702, unique records: 396
total: output=47,356 cache_creation=1,042,774 cache_read=28,112,719 messages=396
OK: agent/model sums match total
```

`tools/token-usage.py` の出力と全項目一致。

## 「3. 書く形」についての見立てへのコメント

実装者の見立て（1 行目のみ archives へ貼る、2 行目の参考は貼らなくて
よい）に検算のうえでも異論は無い。決めるのは管理者。

## コードは直していない

見つけた不具合（`find_start()` が「立てる」コミットと「決着させる」
コミットを区別しない）は報告のみ。修正は行っていない。
