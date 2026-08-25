# TODO-050 の分担

## 誰に何をさせたか

| 担当 | 何を |
|------|------|
| main | 決めること 5 つを利用者と決め、依頼書を書き、報告を受けて判断する |
| implementer | URL・GET 化、POST-Redirect-GET、キーボード操作、テストの直し |
| verifier | 実際に起動して、URL・戻る/進む・リロード・キーボードを試す |
| reviewer | 変更したコードの質を見る |
| wording | このコミットに入る `.md` から、前例の無い語を挙げる |

依頼書は [request-implementer.md](request-implementer.md)。
報告は [implementer-report.md](implementer-report.md)・
[verifier-report.md](verifier-report.md)・[reviewer-report.md](reviewer-report.md)・
[wording-report.md](wording-report.md)。

## その分担にした理由

- **implementer を立てた。**JavaScript・テンプレート・Python・テストの
  4 つにまたがり、移動の仕組みそのものを変える。`CLAUDE.md` の「複数の
  ファイルにまたがる」に当てはまる
- **verifier は、テストでは見られないものがあるので必ず立てた。**戻る/進む・
  リロードでの再送信・キーボードは `AsyncHTTPTestCase` では確かめられない。
  実際にブラウザを動かす必要がある
- **reviewer も立てた。**`CLAUDE.md` の「挙動や分岐が変わる項目には入れる」に
  当てはまる。POST が GET に変わり、`cmd` の分岐も組み替わる。
  TODO-005 で `save()` の挙動が変わったときに reviewer が拾ったような、
  「テストが通ることを見ても出てこない」種類の抜けが出やすいところ

## 決めたこと（着手時に利用者と決めた）

`TODO.md` の「### 決めたこと」に書いた。5 つとも、この項目の作りを左右する。

- URL はクエリ（`/ytsched/?date=...`）
- URL に入れるのは日付だけ（検索・フィルタは `conf.json` のまま）
- 追加・修正・削除のあとは POST-Redirect-GET
- 編集画面も GET にする（保存の POST は残す）
- キーボードは ←/→・Home・`/`・Esc
