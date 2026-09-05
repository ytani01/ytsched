# TODO-184 レビュー依頼（reviewer）

## 対象

作業ツリーの未コミットの変更（`git diff`）。
`src/ytsched/webroot/static/js/main-page.js` と `week.js`。
背景は TODO.md の TODO-184 と `archives/agents/TODO-184/implementer-request.md`。

## 見てほしいところ

- `fillMainHeight()` の中身が正しいか。`minHeight` を空へ戻してから測る
  順序、`fill_h` の式、短くないときに空のままでよいか
- 呼び出す場所と順序。`setActiveWeek()` では `scrollToId()` のあとに置いた。
  `scrollToId()` は `body_h <= win_h` で早く返す作りなので、その前に
  高さを足すと挙動が変わる。この置き方で漏れる経路は無いか
  （`moveActiveMonth()` / 月間表示 / 検索モード / `popstateHdr` など、
  週や中身の高さが変わる他の経路）
- `resize` / `orientationchange` に素で登録している点。読み込み前
  （`elMain` がまだ null）に発火したときどうなるか。モバイルで
  アドレスバーの出入りのたびに何度も走ることの影響（レイアウトの
  読み書きが交互になる）
- `onloadHdr()` に残った `body_h` / `win_h` の計算と、`fillMainHeight()`
  内の再計算が二重になっている点。読み込み時の挙動が変わっていないか
- ファイル冒頭のコメント（外へ出すもの・外から使うもの）の書き方が、
  このリポジトリの他の記述と揃っているか

コードは直さないこと。見つけたことを報告するだけ。
指摘には、どのくらい確かか（実害があるか、気になる程度か）を添える。

## 報告

`archives/agents/TODO-184/reviewer-report.md` に書く。返事は 5 行以内。
