# TODO-174 の分担

| 担当 | 何を任せたか |
|------|--------------|
| main | `mini_cal.html` / `my.css` の変更、キャプチャの確認、テストの修正 |
| [verifier](verifier-report.md) | pytest・lint・型チェック、HTML の実物確認 |
| [runner](runner-report.md) | テストを直したあとの `tests/test_web.py` 再実行 |

## なぜこの分担にしたか

- **実装は main。** 変更は 2 ファイル・20 行ほどの CSS とテンプレートで、
  切り出して依頼するより自分で書くほうが早い。implementer は立てなかった
- **確認は verifier に分けた。** コードを変える項目では規模によらず
  確認を別の担当にする決まり。今回は「caption に付いていた
  `data-action` を span へ移した」ことで、caption を直接クリックして
  いるブラウザテストと、caption の中身を正規表現で取っている
  `test_web.py` が壊れうると分かっていたので、その 2 つを名指しで
  確かめさせた（`test_web.py` の 1 件は実際に落ちた）
- **runner を足したのは、テストを直したあとの再実行のため。**
  判断の要らない「決まったコマンドを走らせて出力を報告する」だけの
  用件で、verifier をもう一度立てるより軽い。走らせたのは
  変更したファイル（`tests/test_web.py`）だけで、全体の pytest は
  verifier が済ませている
