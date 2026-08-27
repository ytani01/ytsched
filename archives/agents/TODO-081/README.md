# TODO-081 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

## この分担にした理由

- **implementer を分けた。** 変更が `handler.py` / `main_handler.py` /
  `edit_handler.py` / `webapp.py` と新しいモジュール、それに
  `tests/helpers.py` を含むテスト 3〜4 ファイルにまたがる。
  複数のファイルにまたがり、実装とテストと文書がまとまって要る規模
- **verifier を分けた。** 「挙動は変えない」項目なので、既存のテストが
  全部通ることと、アプリが実際に起動することを、実装した本人以外が
  確かめる必要がある
- **reviewer を入れた。** `initialize()` は `__init__` のあとに呼ばれる
  という tornado の順序に依存する変更で、関数の移動も 47 か所の
  呼び出しに触る。分岐や初期化の順序が変わる項目には入れる
  （`CLAUDE.md` の基準）

## 報告ファイル

- [implementer への依頼](implementer-task.md)
- [implementer の報告](implementer-report.md)
- [verifier の報告](verifier-report.md)
- [reviewer の報告](reviewer-report.md)
- [wording の報告](wording-report.md)
