# TODO-170 verifier への依頼（2 回目・修正後の確認）

## 経緯

1 回目の確認（`archives/agents/TODO-170/verifier-report.md`）では不具合
ゼロだった。そのあと reviewer の指摘 4 点を反映してコードが変わった
（`archives/agents/TODO-170/implementer-report-2.md`）。変わったのは:

- 空行を `lines_unreadable` に数えず、そのまま書き戻すようにした
- `except (UnicodeDecodeError, json.JSONDecodeError):` に括弧（`# fmt: skip`）
- 未使用の `_log` を削除
- docstring の追記、テストを 4 件追加

## 確かめること（範囲を絞る）

1. `mise run test` を走らせて結果を報告する
   （`fmt` / `typecheck` / `lint` も 1 回ずつ叩いてよい。
   `mise run upgradeproject` は走らせない）
2. **実データのコピーで、1 回目と同じ結果になることだけ確かめる。**
   - `\cp -a ~/ytsched/data <tmp>/data`（`cp` は `-i` にエイリアス
     されているのでバックスラッシュを忘れない）。
     **元の `~/ytsched/data` には絶対に書き込まない**
   - `uv run ytsched fix-id --datadir <tmp>/data --dry-run` の件数が
     1 回目と同じか（走査 6738 / 書き換えファイル 6555 /
     書き換え行 13418 / 元から UUID 6 / 読めなかった行 0）
   - 本番実行して、**全行で `sde_id` 以外が値も並び順も変わって
     いないこと**、行数が変わっていないこと、非 UUID が残っていない
     こと、`sde_id` が全体で一意になっていることを確かめる
   - もう一度実行して 0 件になること
3. **Web アプリの起動確認は省略してよい**（1 回目で済んでいて、
   今回の修正はその経路に関わらないため）

## やらないこと

- **コードを直さない。** 見つけたことは報告に書く
- `TODO.md`・`docs/`・`README.md` は触らない
  （`docs/` は writer が同時に書いている）

## 報告

`archives/agents/TODO-170/verifier-report-2.md` に書く。返事は 5 行以内。
