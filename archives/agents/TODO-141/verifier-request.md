# TODO-141 verifier 依頼

TODO-141 の実装が実際に動くかを、次の範囲だけで確認する。

- `mise run test` を実行し、全体のテスト・lint・型検査結果を記録する。
- `uv run pytest tests/test_browser.py -k 'trash_select' -q` を実行し、
  未選択時の無効化、部分選択、確認のキャンセルと承認、選択した項目だけの
  削除、全選択をブラウザで実測する。
- `uv run pytest tests/test_trash.py tests/test_web.py -q` を実行し、複数削除、
  不正入力、表示外の項目の保持、削除後の遷移を実測する。
- `git diff --check` を実行する。

実データは使わない。ソース、テスト、TODO は変更せず、コミットもしない。
結果は `archives/agents/TODO-141/verifier-report.md` に書く。
