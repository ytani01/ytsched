# TODO-170 verifier への依頼

## 目的

新しく作った `ytsched fix-id`（`src/ytsched/fix_id.py`）が実際に動くかを
確かめる。仕様は `TODO.md` の TODO-170 の節、実装の説明は
`archives/agents/TODO-170/implementer-report.md`。

## 確かめること

1. `mise run fmt` / `typecheck` / `lint` / `test` を走らせて、結果を
   そのまま報告する（`mise run upgradeproject` は走らせない）
2. **実データのコピーで試す。** ここがこの依頼の中心。
   - `~/ytsched/data` を一時ディレクトリへ**コピー**する
     （`\cp -a ~/ytsched/data <tmp>/data`。`cp` は `-i` に
     エイリアスされているのでバックスラッシュを忘れないこと）。
     **元の `~/ytsched/data` には絶対に書き込まない**
   - `uv run ytsched fix-id --datadir <tmp>/data --dry-run` を叩き、
     件数を記録する。**dry-run の後にコピーが 1 バイトも変わって
     いないこと**を確かめる（`diff -r` などで）
   - 続けて `--dry-run` 無しで実行し、次を確かめる:
     - 走査・書き換えの件数が dry-run と一致する
     - **全ファイルの全行で、`sde_id` 以外のキーが値も並び順も
       変わっていない**（各行を `json.loads` して `sde_id` を除いた
       残りを比べる、`sde_id` の値だけ元に戻して `diff -r` を取る、など
       確実な方法で）
     - 実行後、非 UUID の `sde_id` が 1 件も残っていない
     - `sde_id` が全体で一意になっている（走査前は 8 種類が重複していた）
     - `trash.jsonl` が変わっていない
     - 行数がファイルごとに変わっていない
   - もう一度実行して、2 回目は 1 件も書き換わらないことを確かめる
3. 書き換えた後のデータで Web アプリが動くか。
   `uv run ytsched webapp --datadir <tmp>/data -p <空きポート>` を
   起動し、週間表示・検索・編集画面が開くこと、編集して保存できることを
   `curl` で確かめる。**`--datadir` に実データを指定しない**
4. 参考: 着手前に main が数えた実データの値は
   UUID 6 件 / 非 UUID 13418 件 / 非 UUID を含むファイル 6555 個 /
   `.jsonl` 6739 ファイル・13429 行。食い違ったら報告すること

## やらないこと

- **コードを直さない。** 見つけたことは報告に書く
- `TODO.md`・`docs/`・`README.md` は触らない

## 報告

`archives/agents/TODO-170/verifier-report.md` に書く。返事は 5 行以内。
