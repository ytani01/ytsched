# TODO-170. 予定の `sde_id` を UUID に統一する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + writer |
| 消費 | output 59,943 / cache_creation 474,424 / 概算 $5.8 |
|      | main 45% + implementer 26% + verifier 18% + reviewer 7% + writer 5%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-170/](../agents/TODO-170/README.md) にある。

## きっかけ

新しく作る予定の `sde_id` は UUID だが、旧形式から移ってきたものは
独自の形（13〜18 文字）のまま残っていた。実データでは UUID が 6 件、
旧形式が 13418 件で、非 UUID を含むファイルが 6555 個あった。
**旧 ID は 8 種類が重複**しており（最大 3 回）、「ファイル内で
`sde_id` は一意」という前提が崩れる余地があった（TODO-027）。

## やったこと

`ytsched fix-id`（`src/ytsched/fix_id.py`）を作った。全データを走査して、
UUID でない `sde_id` だけを `uuid.uuid4()` へ振り直す。

- 対象は `{年}/{月}/{日}.jsonl` と `ToDo.jsonl`。`trash.jsonl`・`.cgi`・
  `.bak` は触らない
- `sde_id` 以外はキーの並びも値も変えない
- JSON として読めない行はそのまま残して数える
- 書き戻しは一時ファイル → `os.replace`。`.bak` は作らない
  （6555 個の `.bak` が散らばるのを避けた）。変更の無いファイルは書かない
- `--datadir` / `--dry-run` / `--debug` は `migrate`・`holiday` と揃えた

ゴミ箱を対象外にしたのは、ゴミ箱は履歴で、復活のときはどのみち
`sde_id` を振り直していたため（TODO-086）。

reviewer の指摘は 4 点で、いずれも軽いものだった。改行で終わって
いないファイルに改行が付く件は、**利用者が「補う現状のままでよい」と
決め**、docstring とテストで振る舞いを固定した。

## 実データへの適用

**この項目の `fix-id` は、実データに当てる前に TODO-171 で作り直した。**
`sde_id` の末尾にバージョン番号を付けることになり、振り直しの形が
`{UUID}-{版}` に変わったため。実データへは 2026-09-03 に、TODO-171 の
`fix-id` を一度だけ当てて、この項目の分もまとめて済ませた。
6739 ファイル・13429 行を書き換え、読めなかった行は無し。旧 ID の
重複 8 種類も解消した。

## テスト

- `tests/test_fix_id.py` を追加
- verifier に**実データのコピー**で試させた。一時ディレクトリの小さな
  データでは、実データにしか無い形（U+2028 を含む行、euc_jp 由来の
  文字、8 種類の重複 ID）を踏めないため。`sde_id` 以外の不一致 0 件、
  行数のずれ 0 件、書き換え後は 13424 件すべてが相異なる UUID、
  `trash.jsonl` は不変、2 回目の実行は 0 件、書き換え後のデータで
  Web アプリが動き編集・保存もできることを確かめた
- テスト 637 件パス
