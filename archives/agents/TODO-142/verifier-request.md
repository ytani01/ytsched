# TODO-142 verifier 依頼

TODO-142 の実装を次の範囲だけで実測する。

- `uv run pytest tests/test_browser.py -k 'trash_select' -q` を実行する。
- ブラウザテストが、部分選択時にヘッダーが未選択かつ indeterminate でない
  こと、全選択・全解除、削除ボタン、選択した項目だけの削除を確認しているか
  結果とともに確認する。
- `mise run test` を実行する。
- `git diff --check` を実行する。

実データは使わない。ソース、テスト、TODO は変更せず、コミットもしない。
結果は `archives/agents/TODO-142/verifier-report.md` に書く。
