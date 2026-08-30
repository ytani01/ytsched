# TODO-129 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort medium | implementer + verifier + reviewer |

## なぜこの分担にしたか

Python・テンプレート・CSS・テストの 4 ファイルにまたがるので implementer に
分けた。ミニカレンダーが**ファイルを開くようになる**（今まではファイルの
大きさを見るだけだった）のは挙動の変更で、キャッシュの持ち方と噛み合うかを
テストが通ることでは確かめられないので reviewer を入れた。見た目の変更なので
verifier にはキャプチャを撮らせ、色の最終判断は利用者に仰いだ。

## 報告

- [implementer-report.md](implementer-report.md)
- [reviewer-report.md](reviewer-report.md)
- [verifier-report.md](verifier-report.md)（末尾に、グレーを濃くしたあとの
  追加確認がある）
