# TODO-083 reviewer への依頼

`my.js`（1,399 行）を 8 つの `.js` に分け、ファイルをまたぐ状態を
`ytState` オブジェクトにまとめた。**挙動は変えない**という前提の
リファクタリング。

## 先に読むこと

- `TODO.md` の TODO-083、`docs/design-review.md` の I
- `archives/agents/TODO-083/implementer-request.md`（決めた方針）
- `archives/agents/TODO-083/implementer-report.md`

## 見てほしいこと

1. **挙動が変わっていないか。** 元は
   `git show HEAD:src/ytsched/webroot/static/js/my.js` で読める。
   とくに次を疑うこと:
   - `let x;`（`undefined`）→ `ytState.x = null` への変更で、判定が
     変わる箇所が無いか
   - トップレベルの `window.addEventListener(...)` が、元と同じ数・
     同じ順で残っているか（`spinner.js` の `pageshow`、
     `keyboard.js` の `visualViewport`、`main-page.js` の一式）
   - `main.html` から移した `homeButtonHdr()` / `onloadHdr()` /
     `changeSearchN()` の中で、テンプレートの値
     （`url_prefix` / `today_str` / `search_str0`）の置き換えが
     正しいか。**`search_str0`（検索モードか）と `search_str`
     （入力欄の値）を取り違えていないか**
   - `changeSearchN()` の `cur_day.value` →
     `document.getElementById("cur_day").value` が等価か
2. **読み込みの順番。** 素の `<script>` なので、トップレベルで走る
   コードの依存が順番どおりか。`main-page.js` を `base.html` に
   入れていないか（入れると `edit.html` でも `onloadHdr` が走る）
3. **分け方が妥当か。** 別のファイルへ入れたほうがよい関数、
   ファイルをまたぐ参照で見落としているものが無いか
4. **`ytState` に入れるものの線引き。** 1 ファイルに閉じている状態
   （`swipeStart` など）を残した判断が妥当か
5. プロジェクトの決まり（`CLAUDE.md` / `src/README.md`）からの逸脱

## やらないこと

- **コードを直さない。** 見つけたことは報告するだけ。直すかは管理者が決める

## 報告

`archives/agents/TODO-083/reviewer-report.md` に書く。
指摘には「必ず直すべき / 直したほうがよい / 好みの範囲」の区別を付ける。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
