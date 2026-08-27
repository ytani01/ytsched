# TODO-096. Android の Firefox でアイコンが黒く塗りつぶされる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + wording |
| 実施 | Opus 5 / effort high | verifier + wording |
| 消費 | output 21,227 / cache_creation 127,067 / 概算 $3.3 |
|      | main 88% + wording 8% + verifier 4%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-096/`](../agents/TODO-096/README.md) にある。

## きっかけ

Android の Firefox で、アイコンが軒並み黒く塗りつぶされて表示された。
利用者のスクリーンショットでは、フッターの ◀ ▶（`chevron-left` /
`chevron-right`）が黒い三角、虫めがね（`search`）が黒い丸、消去キー
（`backspace`）が黒い矢印になっていた。漏斗（`filter`）と `angle-down`
も黒い三角だった。

いずれも「線画の輪郭が黒く塗られた形」で、`fill: none` と
`stroke: currentColor` が効いていない見え方だった。

## 原因

`icons.svg` は、線画の描き方をファイルの中の `<style>` で `symbol` に
当てていた（TODO-048 で Font Awesome から差し替えたときから）。

```
<defs>
  <style>
    symbol { fill: none; stroke: currentColor; stroke-width: 2; ... }
  </style>
</defs>
```

外部ファイルを `<use href="...icons.svg#id">` で参照すると、中身は
shadow tree になる。参照先のファイルにある `<style>` を適用するか
どうかはブラウザによって差が出て、Firefox for Android では適用され
なかった。その結果 `fill` が既定の黒、`stroke` 無しになり、輪郭の
パスがそのまま黒く塗られた。

## やったこと

線画の描き方を `my.css` の `.my-icon` へ移し、`icons.svg` の
`<defs><style>` を削除した。

```css
.my-icon {
    ...
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
}
```

`fill` / `stroke` / `stroke-width` は継承する CSS プロパティなので、
参照する側の `<svg class="my-icon">` に書けば shadow tree の中まで
届く。`.my-icon-9x` の `stroke-width: 1` は、もともとこの仕組みで
効いていた。

- `.my-icon-9x` は `.my-icon` と詳細度が同じなので、CSS の中での
  前後関係で決まる。`.my-icon` より後ろにあり、`1` が勝つ
- `circle-up-fill` と `dot-circle` の塗りは `fill="currentColor"
  stroke="none"` を要素へ直接書いてあり、継承より優先されるので
  この指定に潰されない
- テンプレートで `icons.svg#` を参照している `<svg>` は 24 か所すべてが
  `class` に `my-icon` を持っている。持たないものがあると、そこだけ
  今度は本当に黒くなる

`icons.svg` と `my.css` の両方のコメントに、なぜここに書くのかを残した。

## テスト

自動テストは足していない。CSS の宣言がどのブラウザで効くかを
`pytest` で見ることはできず、`test_browser.py` の playwright は
Chromium で走るため、そもそも今回の症状が出ない。

verifier が次を確認した。

- `mise run fmt` / `typecheck` / `lint` / `test` が通ること
- `icons.svg` が整形式の XML のままで、`<style>` が残っていないこと
- `my.css` の `.my-icon` に 5 つの宣言が入り、`.my-icon-9x` より
  前にあること
- テンプレートの `<use>` 24 か所すべてに `my-icon` が付いていること
  （verifier の報告は 25 か所とあるが、数え直すと 24。漏れが無い
  という結論は変わらない）
- アプリを起動して `my.css` と `icons.svg` が 200 で配信されること

main は headless の Chromium でメイン画面と編集画面を描画し、
アイコンが線画で出ること（`dot-circle` の中心の塗りが残っていることを
含む）を目視で確かめた。**Android の Firefox での確認は利用者による。**
