# TODO-181 の分担

|          | 担当 | 何を任せたか |
|----------|------|--------------|
| 実装     | main | `_double_tap_home_in_search()` の `assert` → 条件付き `pytest.skip()` と docstring の書き直し |
| 確認     | verifier | lint、ダブルタップ系テストの 3 回実行、skip 分岐のスクラッチ確認 |

直すのは `tests/test_browser.py` の 1 関数の数行なので、implementer は
立てずに main が書いた。テストの失敗のしかたが変わる（fail → 条件付き
skip）ので、確認は verifier に分けた。reviewer は入れていない
（分岐は 1 つ増えるだけで、挙動はテストの内部にとどまる）。

verifier の結果: lint 通過、`-k "double_tap or home_button"` が 3 回とも
13 passed / 0 skipped / 0 failed（AssertionError なし）。skip 分岐は
スクラッチで確認（`interval_msec=10` で「機械が混雑:」の `Skipped`、
`interval_msec=100000` で最後まで到達）。

verifier が挙げた懸念（依頼 4）: 検索画面の読み直しが恒常的に遅くなる
リグレッションが入ると、`interval_msec` = 500 / 600 の経路は fail では
なく skipped に変わり、退行を黙って見逃す余地がある。TODO-165 の
reviewer 指摘 3 と同じ論点。線引きは「混雑時に限る・理由付きで skipped
件数に出す」までで、恒常的に skip が出るようになったら読み直しの速度を
疑う、という扱いにした（TODO 側にも記載）。

- [依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)

TODO 側は
[archives/todo/TODO-181. ダブルタップのテストが、機械の負荷が高いと落ちる.md](../../todo/TODO-181.%20ダブルタップのテストが、機械の負荷が高いと落ちる.md)。
