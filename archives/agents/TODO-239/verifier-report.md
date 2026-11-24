# TODO-239 verifier 報告

結論: **起きる。** 同じ名前で付け直した画像は、同じ Playwright context では古い寸法（10x10）のまま表示され続けた（goto 3/3、通常操作 3/3）。

## 方法
- スクリプト: `archives/agents/TODO-239/measure.py`（`uv run python archives/agents/TODO-239/measure.py`）。`--datadir` は一時ディレクトリ
- 画面操作だけで行った（`attachments/` の直接置き換えはしていない）: 編集画面で title を入れ、10x10 の `a.png` を `set_input_files` → 更新ボタン。ファイルの mtime を `os.utime` で 30 日前に
- 同じ context で詳細を開いて画像を読む（3 回）。その後、編集画面で「外す」にチェック＋40x30 の `a.png` を選んで更新。付け直し後のファイル名は `a.png` のまま（`attachments/<uuid>/a.png`、98 バイト、mtime は直前＝新しい）
- 画像のサーバ要求の有無は、CDP の `Network.requestServedFromCache` と、Playwright の `response.headers` で見た。サーバのアクセスログは 200 を出さないので使えなかった

## 計測値
| 場面 | 回数 | naturalWidth x Height | 要求の扱い |
|---|---|---|---|
| 付ける前、goto | 3 | 10x10 ×3 | 1 回目は要求が出た（servedFromCache 無し）、2・3 回目は servedFromCache |
| 付け直し後（期待 40x30）、goto | 3 | **10x10 ×3（古い）** | 3 回とも servedFromCache |
| 付け直し後、編集画面→戻るボタン→詳細を開く | 3 | **10x10 ×3（古い）** | 3 回とも servedFromCache |

- 付け直し後の応答ヘッダ（Playwright が見た 3+3 回すべて）: `last-modified: Sun, 25 Oct 2026 21:09:45 GMT`（30 日前の旧ファイルの値）。`etag`・`cache-control` は無し
- ディスク上の新ファイルの Last-Modified はそれと違う（mtime は付け直した時刻）ので、応答は旧ファイルのキャッシュ
- 注意: 付け直し後に `Network.responseReceived` は `status 200, fromDiskCache=False` と出ているが、同時に servedFromCache も出ている。サーバへ届いたかどうかは、この 2 つからは決めきれない。ただし寸法と Last-Modified が旧ファイルのものなので、少なくとも新しい内容は来ていない

## 確かめていないこと
- 他のブラウザ、context を作り直した場合、時間が経ったあとのキャッシュ失効
- 旧ファイルの mtime が新しい（数分前）場合に出るか（今回は 30 日前の条件のみ）
- 原因の切り分けと直し方は見ていない（依頼どおり）
