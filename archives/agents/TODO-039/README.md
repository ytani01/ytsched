# TODO-039 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer + wording |

## 誰に何を任せたか

| 担当 | 範囲 |
|---|---|
| main | アイコンのデザインと画像の生成、`tools/make-icons.sh`、依頼書、`TODO.md`、archives |
| implementer | `manifest.json`、`base.html` の `<head>`、キーボード追従の JavaScript と CSS、テスト、`README.md` |
| verifier | テスト・lint・build、起動確認、配信とパッケージの中身の確認 |
| reviewer | キーボード追従の JavaScript |
| wording | このコミットに入る `.md` |

## そうした理由

- **アイコンだけは main が作った。** 見た目を決める作業で、描いたものを
  実際に見て、小さくしても形が残るかを確かめながら進める必要がある。
  main は画像を読めるので、候補を 3 つ描いて利用者に見せ、選んでもらう
  ところまでを一続きでできる。担当に渡すと、この往復のたびに報告と依頼を
  書き直すことになる
- **implementer を分けたのは、触るファイルが多いから。** テンプレート・
  JavaScript・CSS・新規の JSON・テスト 2 ファイル・README にまたがる。
  基準（複数のファイルにまたがる、実装とテストと文書がまとまって要る）に
  当てはまる
- **reviewer を入れたのは、挙動が変わるから。** `visualViewport` を見て
  バーの位置をずらす処理は、条件（キーボード・ピンチ・回転）で分岐する。
  テストでは捕まらない種類の間違いが入りやすい。`CLAUDE.md` の
  「挙動や分岐が変わる項目には入れる」に当てはまる
- **verifier は、試せる手順があるので分けた。** アイコンと manifest が
  実際に 200 で返るか、wheel に入るか、`start_url` の相対が意図どおり
  解決されるかは、走らせないと分からない
- **wording は `.md` が入るので必ず立てる。**

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)
- [wording-report.md](wording-report.md)

依頼書は [implementer-request.md](implementer-request.md)。
