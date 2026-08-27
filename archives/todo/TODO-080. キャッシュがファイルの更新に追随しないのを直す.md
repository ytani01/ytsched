# TODO-080. キャッシュがファイルの更新に追随しないのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 13,307 / cache_creation 203,060 / 概算 $5.1 |
|      | main 69% + verifier 13% + reviewer 8% + implementer 7% + wording 4%（料金の割合） |

## きっかけ

基本設計のレビュー（`docs/design-review.md` の C）で挙がった。

`SchedData._sdf_cache` はファイルの更新時刻を見ていなかったので、
`ytsched migrate` を走らせても、手でファイルを直しても、サーバが
生きている間は古い内容を返し続けていた。ホームボタンのダブルタップは
DOM を取り直すだけなので、サーバ側は古いまま。

## やったこと

- `SchedDataFile` が、読み込んだときの `(st_mtime, st_size)` を
  `_stat_key` に持つ。ファイルが無いときは `None`
- `SchedDataFile.is_stale()` が、今のファイルと見比べて変わっているかを
  返す。`os.stat()` は 1 回だけで、`OSError`（消えた・権限が無い）は
  「変化あり」として扱う
- `SchedData.get_sdf()` が、キャッシュに当たっても `is_stale()` なら
  読み直す（新しい `SchedDataFile` を作って差し替える）
- `SchedDataFile.save()` が、書いたあとに `_stat_key` を持ち直す。
  `SchedData.save()`（TODO-077）の直後に読み直しが起きないようにするため

**`st_mtime` だけでなく `st_size` も見る。** 同じ秒の中で書き換えると
`mtime` が変わらないことがあるため。ファイルが無いときを `None` に
してあるので、**無かった日のファイルがあとからできたとき**も読み直せる。

### `DEF_CACHE_SIZE` を 20,000 から 2,000 へ

20,000 は、TODO-069 で 1 リクエストが 63 日ぶんを読むようになる前の
数字で、根拠が見えなかった。2,000 の根拠は 2 つ。

- `LoadMonths` の上限 24 ヶ月（前後 2 年）だと、1 リクエストで
  207 週 × 7 日 + ToDo = **1,450 件**
- 検索モードは 1 件も当たらないと最大 `SEARCH_MODE_MAX_DAYS`
  （**1,825 日**）さかのぼる（データファイルが無い日は開かない。TODO-028）

大きいほうに余裕を持たせた。実装者は前者だけを見て 1,500 にしていたが、
自分で「検索モードはこれより大きい」と気づいて報告に書いていたので、
main が 2,000 に直した。

## テスト

`tests/test_ytsched.py` に 5 本足した。

- 外から書き換えると、次の `get_sdf()` で新しい内容が返る
- 変えていなければ読み直さない
- キャッシュに載ったあとファイルが消えても落ちない
- 無かった日のファイルがあとからできたら読める
- `save()` の直後に無駄な読み直しが起きない

**最後の 1 本は、最初は狙った退行を捕まえられなかった**（reviewer の
指摘）。新しく作るファイルは `add_sde()` の時点でまだ無く `_stat_key`
が `None` なので、読み直しが起きるのは `save()` 直後の 1 回目。
`save()` のあとから見ていては遅い。見る位置を前へ動かし、
`save()` の `_stat_key` の持ち直しを外すと落ちることを確かめた。

`mise run lint` 通過。`uv run pytest tests` 465 passed。

verifier が、**サーバを動かしたまま**外からファイルを書き換えて画面に
反映されること、直す前は古いままであること、`ytsched migrate` のあと
再起動せずに新しいデータが見えることを確かめた。

分担と報告は [`archives/agents/TODO-080/`](../agents/TODO-080/README.md)。
