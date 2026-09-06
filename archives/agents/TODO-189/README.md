# TODO-189 の分担

`.gitignore` に `.codegraph/` を 1 行足すだけの項目。

| 担当 | モデル | 依頼したこと |
|------|--------|--------------|
| main | Opus 5 / effort high | `.gitignore` の追記、TODO と archives の記述 |
| verifier | Haiku 4.5 | 無視ルールが意図どおり効いているかの確認 |

## この分担にした理由

- **implementer は立てなかった。** 変更は 1 ファイル 1 行で、
  他のファイルにまたがらない
- **reviewer は立てなかった。** 挙動が変わる項目ではあるが、分岐も
  条件式も無い。見るべきは「効いているか」だけ
- **verifier は分けた。** `.gitignore` は、書いたつもりの行が別の行に
  拾われていたり、追跡中のファイルを巻き添えにしていたりする。
  実際にコマンドで試せるので、`CLAUDE.md` の「試せる手順があるなら
  分ける」に当たる
- **verifier のモデルは定義の sonnet から Haiku 4.5 に下げた。**
  `git status` と `git check-ignore` の出力を読むだけで、判断が要らない

## 報告

- [verifier の報告](verifier-report.md)
