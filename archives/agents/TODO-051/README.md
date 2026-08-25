# TODO-051 の分担

**この項目は保留になった**（症状が再現しなかったため）。実際に直したのは
`tools/screenshot.py` の `DEF_URL` だけ。経緯は `TODO.md` の TODO-051 の節にある。

## 誰に何をさせたか

| 担当 | 何を |
|------|------|
| main | 症状の再現を試み、`DEF_URL` の変更、`TODO.md`・`docs/Developer.md` の記述 |
| verifier | 変更後に一覧・編集画面が撮れることの確認（`DISPLAY` のあり／なし両方）、lint・型チェック・テスト |
| wording | このコミットに入る `.md` から、前例の無い語を挙げる |

報告は [verifier-report.md](verifier-report.md)・[wording-report-2.md](wording-report-2.md)。
[wording-report.md](wording-report.md) は、この項目を**立てたとき**のもの。

## その分担にした理由

- **実装が数行なので、implementer は立てず main が直した。**変えたのは定数 1 つと
  文書 2 か所で、複数のファイルにまたがる作りの話は出てこない
- **verifier は、項目が小さくても分けた。**確かめる手順（`DISPLAY` のあり／なしで
  実際に撮る、404 と 200 を対比する）がはっきりしていて、試せることがある。
  書式を見るだけの確認なら main で済ませるが、今回は当てはまらない
  （`CLAUDE.md` の「試せる手順があるなら分ける」）
- **`.md` が 2 つ入るので wording を立てた。**`TODO.md` に「保留」「環境依存」など、
  これまで使っていない言い方が入った

## verifier が出した、範囲外の指摘

`tools/screenshot.py` は HTTP のステータスを見ずに撮るので、**404 のページでも
そのまま PNG を保存する**（旧既定の `/edit/` で実際に起きた）。今回の変更で
編集画面は撮れるようになったが、URL を間違えたときに気づけない点は残っている。
直すかどうかは、この項目とは別に決める。
