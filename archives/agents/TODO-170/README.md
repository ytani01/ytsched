# TODO-170 の分担

| 担当 | 依頼した内容 | 依頼書 | 報告 |
| --- | --- | --- | --- |
| implementer | `fix_id.py`・`fix-id` サブコマンド・テストの実装 | [implementer-brief.md](implementer-brief.md) | [implementer-report.md](implementer-report.md) |
| verifier | 実データのコピーでの動作確認、テスト・lint | [verifier-brief.md](verifier-brief.md) | [verifier-report.md](verifier-report.md) |
| reviewer | データを失う道が無いかを中心にコードレビュー | [reviewer-brief.md](reviewer-brief.md) | [reviewer-report.md](reviewer-report.md) |
| implementer | reviewer の指摘のうち、main が直すと決めた 4 点の反映 | [implementer-brief-2.md](implementer-brief-2.md) | [implementer-report-2.md](implementer-report-2.md) |
| verifier | 修正後に 1 回目と同じ結果になるかの確認 | [verifier-brief-2.md](verifier-brief-2.md) | [verifier-report-2.md](verifier-report-2.md) |
| writer | `docs/` と `src/README.md` への反映 | [writer-brief.md](writer-brief.md) | [writer-report.md](writer-report.md) |

## この分担にした理由

立てたときの見込みは `implementer + verifier + reviewer`。

**reviewer を入れたのは、全データを一括で書き換えるコマンドだから。**
6555 ファイル・13418 行を書き換える処理で、書き戻しを 1 箇所間違えると
実データが消える。テストが通ることを見ても、行を失う道があるかどうかは
出てこない。

**verifier に実データのコピーで試させたのが中心。** 一時ディレクトリに
作った小さなデータでは、実データにしか無い形（U+2028 を含む行、euc_jp
由来の文字、8 種類の重複 ID）を踏めない。`\cp -a` でコピーして、
`sde_id` 以外が 1 文字も変わっていないことを全 13424 行で確かめさせた。

**writer は見込みに入れていなかった。** 着手してみると直す文書が
`docs/data-format.md`・`docs/Install.md`・`docs/Developer.md`・
`src/README.md` の 4 つあり、それぞれ既存の節の書き方に揃える必要が
あったので分けた。

## 結果

- verifier（1 回目）: 不具合ゼロ。実データのコピーで
  6555 ファイル・13418 行を書き換え、`sde_id` 以外の不一致 0 件、
  行数のずれ 0 件、書き換え後は 13424 件すべてが相異なる UUID
  （**8 種類あった重複も解消**）、`trash.jsonl` は不変、2 回目の実行は
  0 件、書き換え後のデータで Web アプリが動き編集・保存もできた
- reviewer: **データを失う道は無し。** 指摘は 4 点で、いずれも軽い
  1. 末尾が改行で終わっていないファイルに改行が付く
     → **利用者が「改行を補う現状のままでよい」と決めた。**
     docstring とテストで振る舞いを固定した
  2. `except A, B:`（括弧なし）は Python 3.14 では正しく動くが
     誤解されやすい → 括弧を付けた。ただし `ruff format` が
     Python 3.14 の文法として括弧を剥がすので `# fmt: skip` で固定
  3. 未使用の `_log` → 消した
  4. 空行が「読めなかった行」に数えられる → `is_empty_line()` で
     別扱いにした
- verifier（2 回目）: 修正後も 1 回目と完全に同じ結果。テスト 637 件パス

## 気づいたこと

**reviewer の指摘 1 は、依頼書で名指しした観点がそのまま当たった。**
「元のファイルに無かった改行を足していないか」と書いておいたところ、
再現コードまで書いて確かめてきた。見てほしい観点を具体的に挙げると
効く。
