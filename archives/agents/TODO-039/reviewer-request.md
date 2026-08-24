# TODO-039 reviewer への依頼

見てほしいのは **`static/js/my.js` に足した `followKeyboard()` と、その
登録のしかた**（`my.js` の末尾）。ソフトキーボードが出たときに、画面下に
固定したバーを持ち上げる処理。

`verifier` が「動くか」を見るので、あなたは「良いか」を見てほしい。

## 変更の範囲

```sh
git diff -- src/ytsched/webroot/static/js/ \
            src/ytsched/webroot/static/css/ \
            src/ytsched/webroot/templates/ \
            src/ytsched/webroot/static/manifest.json
```

`manifest.json` は新規なので `git status` で拾う。

背景は
[implementer-request.md](implementer-request.md) と
[implementer-report.md](implementer-report.md)。

## 特に見てほしいところ

- **`gap` の計算が、どういう状態で狂うか。**
  `window.innerHeight - vv.height - vv.offsetTop` で、キーボードの高さを
  出しているつもりでいる。回転したとき、ページを拡大したまま
  キーボードを出したとき、`vv.offsetTop` が動いている最中、アドレスバーが
  隠れたとき——どれかで意図しない値にならないか
- **`transform` を直に書き換えていること。** 対象の要素
  （`main.html` の `#menu_bar`、`edit.html` の `#menu`）に、他から
  `transform` が当たっていないか。`.my-bar-content` は `bottom` と
  `transition: all 0.05s` を使っているが、こちらは対象外にしてある
- **`scale <= 1.01` という書き方。** ピンチ拡大を除くための条件だが、
  この閾値でよいか。`vv.scale` が `undefined` の環境で
  `undefined <= 1.01` が `false` になり、**ずらす処理が丸ごと止まる**
  ことに気づいているか
- **登録のしかた。** `my.js` はこれまで関数定義と変数宣言だけで、
  末尾で `addEventListener` を呼ぶのは初めて。`base.html` の `<head>` で
  `defer` 無しで読まれる。`load` に間に合うか、二重に登録されないか
- `manifest.json` の `start_url` / `scope` を `../` にしていること。
  `--urlprefix` を変えても付いてくるようにするためだが、
  **抜けがないか**（`/` で開いたときは scope の外になる、など）
- `.my-follow-keyboard` が中身の空の CSS ルールになっていること。
  目印として置いているが、これでよいか

## 見なくてよいもの

- **アイコンの画像と `tools/make-icons.sh`**（main が作った。範囲外）
- 行長やインデントのような、機械で見るもの
- 実機のスマホでしか分からないこと（利用者が確かめる）

## 決まりごと

- **コードを直さない。** 指摘するだけ
- **確信度の高い指摘に絞る。数を稼がない**
- 報告は `archives/agents/TODO-039/reviewer-report.md`
