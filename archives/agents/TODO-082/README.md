# TODO-082 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |

## この分担にした理由

- **implementer を分けた。** 中身は小さいものの、`src` 5 ファイル・
  テスト 2 ファイル・設定 2 ファイル・文書 2 ファイルにまたがる。
  複数のファイルにまたがる規模（`CLAUDE.md` の目安）
- **verifier を分けた。** 「挙動は変えない」項目で、確かめる手立てが
  はっきりある（テスト、`--help`、実際の起動、ruff の設定を移す前後で
  結果が変わらないこと）。書式の確認だけではないので main では見ない
- **reviewer は入れなかった。** 分岐も初期化の順序も変えていない。
  消したもの・移したものが正しいかは、grep とテストで見切れる

## 判断が要る点は、着手前に利用者へ聞いた

項目には決めきれていない点が 3 つ残っていたので、着手前にまとめて聞き、
答えを依頼書の冒頭に書いてから implementer を起動した。

1. `__init__.py` の import をやめる（`migrate.py` のコメントは変えない）
2. `_app` / `_req` と `filename` / `dirname` は消し、`get_keys()` は残す
3. `x_data1` は消す

## 報告ファイル

- [implementer への依頼](implementer-request.md)
- [implementer の報告](implementer-report.md)
- [verifier への依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)
- [wording の報告](wording-report.md)
