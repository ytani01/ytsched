# TODO-096 verifier への依頼

## 変更の内容

Android の Firefox で、アイコンが黒く塗りつぶされて表示される件の修正。

線画のスタイル（`fill: none` / `stroke: currentColor` / `stroke-width: 2` /
`stroke-linecap` / `stroke-linejoin`）を、`icons.svg` の中の `<style>` から
`my.css` の `.my-icon` へ移した。`icons.svg` の `<defs><style>` は削除した。

外部ファイルを `<use href="...icons.svg#id">` で参照すると中身は shadow
tree になり、参照先のファイルにある `<style>` を適用するかどうかは
ブラウザによって差が出る。参照する側の `<svg class="my-icon">` に書けば、
`fill` / `stroke` / `stroke-width` は継承するプロパティなので中まで届く。

変更したファイル:

- `src/ytsched/webroot/static/css/my.css`
- `src/ytsched/webroot/static/icons/icons.svg`

## 確かめてほしいこと

1. `mise run fmt` / `typecheck` / `lint` / `test` が通ること
2. `icons.svg` が整形式の XML であること（`<defs><style>` の削除で
   壊していないか。`python3 -c "import xml.etree.ElementTree as E;
   E.parse(...)"` などで）
3. `icons.svg` に `<style>` が残っていないこと
4. `my.css` の `.my-icon` に `fill: none` / `stroke: currentColor` /
   `stroke-width: 2` / `stroke-linecap: round` / `stroke-linejoin: round`
   が入っていること
5. **`.my-icon-9x` の `stroke-width: 1` が、`.my-icon` の `2` に
   負けていないこと。** 詳細度が同じなので、CSS の中での前後関係で決まる。
   `.my-icon` より後ろにあるか確かめる
6. **テンプレートの中で `icons.svg#` を `<use>` で参照している
   `<svg>` 要素が、すべて `class` に `my-icon` を持っていること。**
   持たないものがあると、そこだけ今度は本当に黒くなる。
   `src/ytsched/webroot/templates/*.html` を全部見ること
7. アプリを起動して、`/static/css/my.css` と `/static/icons/icons.svg`
   が 200 で配信され、中身が上のとおりであること。
   **起動時は `--datadir` に一時ディレクトリを必ず指定する**

## 報告

`archives/agents/TODO-096/verifier-report.md` に書くこと。
コードは直さないこと。見つけたことは報告だけしてほしい。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内で。
