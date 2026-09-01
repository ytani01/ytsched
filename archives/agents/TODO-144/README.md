# TODO-144 の分担

| 担当 | 範囲 |
| --- | --- |
| main | 仕様管理、CSS・テンプレート・テストの実装、完了記録、コミット |
| verifier | テスト・lint・型チェックと、アプリを起動しての表示確認 |

CSS 1 行・テンプレート 1 行・テストの正規表現 2 か所だけの小さな変更
なので、実装は main が行った。ただし「下線が消えたか」「文字が大きく
なったか」は起動して HTML を見ないと分からないので、確認は verifier に
分けた。分岐の変更が無いため reviewer は立てていない。

verifier は `ruff format --check` が `tests/test_web.py` の変更 2 行を
unformatted と出すことを見つけた。main が `ruff format` を掛けて解消した。

依頼と報告:

- [verifier-request.md](verifier-request.md)
- [verifier-report.md](verifier-report.md)
