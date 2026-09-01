# TODO-142 implementer 依頼

`TODO.md` の TODO-142 の範囲だけを実装する。

## 変更内容

- `src/ytsched/webroot/static/js/trash-page.js` で、一部の項目だけが選択された
  ときも `#trash-select-all` を indeterminate にせず、未選択表示にする。
- 全項目を選択したときはヘッダーを選択済みにする。
- ヘッダーを操作したときの全選択・全解除、削除ボタンの有効化、選択件数、
  一括削除は変えない。
- `tests/test_browser.py` を更新し、部分選択では未選択かつ indeterminate で
  ないこと、全選択、全解除を確認する。

## 制約と確認

- 実データを使わない。
- `TODO.md` と利用者向け文書は変更しない。
- コミットしない。
- 対象ブラウザテスト、JavaScript の整形・ESLint、`git diff --check` を実行する。
- 詳細を `archives/agents/TODO-142/implementer-report.md` に書き、最終応答は
  5 行以内にする。
