# TODO-108. HTML テンプレートのインラインイベントハンドラをイベント委譲へ移行

|      | main | 担当 |
|------|------|------|
| 見込み | Gemini 3.7 Flash / effort medium | implementer + verifier + reviewer |
| 実施 | GPT-5 / effort high | main + implementer + verifier + reviewer |

## きっかけ

HTML テンプレート内のインラインイベントハンドラをなくし、テンプレートを
読みやすく保守しやすくする。

分担と各担当の報告は
[archives/agents/TODO-108](../agents/TODO-108/README.md) にまとめた。

## やったこと

- `main.html`、`sde.html`、`edit.html` の `onmousedown`・`onchange` を
  `data-action` と必要な引数の `data-*` 属性へ置き換えた。
- 一覧と編集画面の親要素で `mousedown`・`change` を受け、操作ごとに既存の
  `window.ytsched` の関数を呼ぶようにした。
- `url_prefix` と一覧用の初期値を `data-*` 属性から読み、テンプレート内の
  設定用インラインスクリプトもなくした。
- スワイプ後のクリック復帰を `data-action` 要素へのイベント送出に替え、
  合成イベントをスワイプ開始として扱わないようにした。
- テンプレートにインラインイベントが残らないこと、日付欄から編集画面へ移動し
  戻れること、引用符を含む検索語でも `data-*` 属性が壊れないことをテストした。

## テスト

- `.venv/bin/pytest tests --ignore=tests/test_browser.py -q`: 483 passed。
- `.venv/bin/pytest tests/test_browser.py -q`: 26 件を 5 回に分けて全件合格。
- `mise run lint`: 合格。
- verifier: 一時データディレクトリで一覧・編集画面を取得し、どちらも HTTP 200、
  テンプレート構文とインラインイベント属性が残らないことを確認。
- reviewer: 検索語の属性エスケープを確認し、再レビューで指摘なし。
