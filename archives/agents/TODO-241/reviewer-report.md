# reviewer 報告 TODO-241

要修正: 無し / 検討: 無し

確認したこと（読んで判断。実行はしていない）:
- `{% set %}` を for の中で使う書き方は sde.html 167 行と同じ。autoescape も、`url_prefix + url_path` を 1 回エスケープするだけで、元の 2 つの `{{ }}` と結果は同じ
- 「外す」チェックボックス、`target="_blank" rel="noopener"`、画像でない添付（リンクだけ）は変わっていない
- テストは `<img src=` が edit に出ること、pdf に出ないことを見ている。`<img>` を外すと失敗する。`is_image` の判定を消して全部に出しても、pdf の否定で失敗する
- CSS の `.my-edit-attach-file` は edit.html 162 行に存在する

確信度が低い／実害は未確認:
- `alt=""` は sde.html（`alt="{{ name }}"`）と違う。リンク内にファイル名の文字があるので、読み上げ上はこちらが適切。揃えるかは好みの範囲
