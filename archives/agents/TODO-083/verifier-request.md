# TODO-083 verifier への依頼

`my.js` を 8 つの `.js` に分け、`main.html` の `<script>` を
`main-page.js` へ移した。**挙動を変えていないこと**を確かめる。

## 先に読むこと

- `archives/agents/TODO-083/implementer-request.md`（何を決めて頼んだか）
- `archives/agents/TODO-083/implementer-report.md`（実装者の報告）

## 確かめること

1. `mise run test`（`uv run pytest`）が全部通る。とくに
   `tests/test_browser.py` は 1 件も skip されずに通ったか
   （chromium が無いと丸ごと skip される。skip されたなら、
   そう報告すること。「通った」と書かない）
2. `mise run lint` / `mise run typecheck` / `mise run fmt --check` 相当
3. **アプリを実際に起動して、ブラウザで動かす。**
   `--datadir` には必ず一時ディレクトリを指定する（実データを汚さない）
   - 週表示が出るか（`#main` が visible になるか）
   - ブラウザのコンソールにエラーが出ていないか（`ReferenceError`、
     404 が最重要。`.js` を 8 本読むようにしたので、
     **どれか 1 本でも 404 になれば、テストが 1 件も落ちないまま
     画面が動かなくなる**）
   - 8 本すべてが 200 で返っているか（`/ytsched/static/js/*.js`）
   - 編集画面（`edit/`）も開いて、同じくコンソールを見る
4. `git show HEAD:src/ytsched/webroot/static/js/my.js` と、新しい 8 本を
   突き合わせて、**関数・定数の中身が `ytState.` を付ける以外に
   変わっていないか**を見る（並べ替え・改名・削除が無いか）
5. 元の `my.js` にあった関数・定数が、1 つも欠けずにどれかのファイルに
   入っているか

## やらないこと

- コードを直さない。見つけたことは報告するだけ
- `mise run upgradeproject` は走らせない

## 報告

`archives/agents/TODO-083/verifier-report.md` に書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
