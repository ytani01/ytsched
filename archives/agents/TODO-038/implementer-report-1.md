# TODO-038 implementer 報告（1 段目・片付け）

依頼書: `archives/agents/TODO-038/implementer-request-1.md`
（**実物は `src/ytsched/webroot/archives/agents/TODO-038/implementer-request-1.md`
に置かれていた。下の「main の判断が要る点」を参照**）

1 段目（消すもの・直すもの）は依頼書の 1〜6 をすべて実施した。
`style` 属性を CSS へ寄せる書き換えには手を付けていない（2 段目の範囲）。

## 変更したファイル

| ファイル | 要点 |
|---|---|
| `src/ytsched/webroot/templates/base.html` | 27 行目の重複した `<title>` を削除。`my_cookie.js` の `<script>` を削除 |
| `src/ytsched/webroot/templates/sde.html` | 50-51 行目の `<input id="sde_id" ... type="hidden">` を削除 |
| `src/ytsched/webroot/templates/main.html` | `id="menu-content"` 2 か所を削除（`class` はそのまま）。`doPost({{ url_prefix }}, …)` と `doPost({{ url }}, …)` の第 1 引数に `'` を付けた |
| `src/ytsched/webroot/templates/edit.html` | `clearBusyFlag()` を削除。`const detail_h` → `let detail_h` |
| `src/ytsched/webroot/static/css/my.css` | `@keyframes blinkborder` / `.blinkborder` / `.my-osd` / コメントアウトされた `.longtext:focus` / 空の `.longtext-sw-label {}` を削除（112 → 75 行） |
| `src/ytsched/webroot/static/js/my.js` | `getBottomDateString()` / `doGet()` / `editStr()` を削除（477 → 424 行） |

## 削除したファイル

`git rm` した（履歴には残る）。

- `src/ytsched/webroot/static/css/pagetop.css`
- `src/ytsched/webroot/static/js/my_cookie.js`

## 消す前に自分で確かめたこと

依頼書の「自分でも確かめること」に対応する。`src/` と `tests/` 全体を
grep して、参照が定義そのものだけであることを確認した。

- `sde_id` — `sde.html` の hidden input は `<form>` の外。JS からも
  `getElementById("sde_id")` の類いは無い（`getElementById` の grep で
  ヒットするのは `main.html:82` の `sde_align` だけ）。予定の ID は
  `doPost(..., {sde_id: '…'})` として `onmousedown` に直接埋まっており、
  hidden input は使われていない。`edit.html:301` の同名 input は編集
  フォームの中にあるので、そちらは残した
- `menu-content` — CSS・JS・Python・テストのどこからも参照なし
  （`#menu-sw` は別物で、`my.css:28` で使っている）
- `.blinkborder` / `.my-osd` — 参照なし。`.blink`・`@keyframes blink`
  （`class_blink`）と `.my-osd-base`（`main.html` の `my-gage`）は使って
  いるので残した
- `.longtext-sw-label {}` — 空の宣言だけを消した。要素側の
  `class="… longtext-sw-label"`（`sde.html:193`）と、
  `.longtext-sw:checked ~ .longtext-sw-label`（`my.css:69`）は残っている
- `getBottomDateString()` / `doGet()` / `editStr()` / `clearBusyFlag()`
  — いずれも定義 1 か所のみ。`busyFlag` 自体は残した
- `pagetop` — `.pagetop` を使う要素も、`pagetop.css` を読む行も無い
- `MyCookie` — `new MyCookie` は 0 件。参照は `my_cookie.js` 内の
  クラス定義とコメントだけ

削除後に再度 grep し、残っているのは意図して残した
`.my-osd-base` と `.longtext-sw-label`（`:checked ~` 側とラベル要素）
だけであることを確認した。

## 確かめた結果

- `mise run fmt` — `25 files left unchanged` / `All checks passed!`
- `mise run lint` — basedpyright `0 errors, 0 warnings`、mypy
  `Success: no issues found in 20 source files`
- `mise run test` — `412 passed`
- `node --check src/ytsched/webroot/static/js/my.js` — OK
- **起動確認**（ポート 10096、`--datadir` は一時ディレクトリ。
  `~/ytsched/data` は使っていない。ポート 12345 には触れていない）
  - `/ytsched/` 200、`/ytsched/edit/` 200、
    `/ytsched/static/css/my.css` 200、`/ytsched/static/js/my.js` 200
  - `/ytsched/static/js/my_cookie.js` と
    `/ytsched/static/css/pagetop.css` は 404（消したので当然）
  - 予定を 1 件 POST で追加し、一覧に出ること、`blink` が付くことを確認
  - 生成 HTML で `<title>` が 1 個、`id="sde_id"` が 0 個、
    `menu-content` が 0 個、`my_cookie` が 0 個
  - `doPost('/ytsched/', …)` と引用符が付いていること
  - 一覧・編集の両方で、`id="…"` の重複が 0 件
- **ブラウザの JS の例外**（`chromium --headless --enable-logging=stderr
  --dump-dom`。Playwright は入っていないので chromium を直接使った）
  - 一覧 740x360 / 412x915、編集 740x360 / 412x915 の 4 通りで
    `Uncaught` / `TypeError` は 0 件。出ているのは元々の
    `console.log` だけ
  - 編集画面の `detail` の高さ: 740x360 で `height: 100px`、
    412x915 で `height: 401px`。`detail_h` の下限 100 が効いている

`detail_h` の修正前の挙動も念のため node で確かめた。

```
before(const): TypeError: Assignment to constant variable.
after(let): detail_h = 100
```

## 自分で決めたこと

- **`edit.html` の `// setTimeout(clearBusyFlag,30000);`（コメント）も
  一緒に消した。** 依頼書には「`clearBusyFlag()` も消す」としか書いて
  いないが、消した関数を指すコメントだけ残すと、次に読む人が
  「どこかにあるはず」と探すことになるため。`busyFlag` の宣言と
  `submitCmd()` 側の使用はそのまま
- **`menu-content` は `id` 属性だけを消し、`<div>` と `class="row m-1"`
  は残した。** 依頼書の「両方とも id を消す」に沿った最小の変更。
  見た目は変わらない
- **`main.html:269` の `{{ obj }}` には引用符を付けていない**
  （依頼書のとおり）。Python の dict が JS のオブジェクトリテラルとして
  出ている。なお展開結果は `{&#x27;date&#x27;: …}` と HTML
  エスケープされているが、これは元からで、属性値なので HTML パーサが
  `'` に戻してから JS が読む。今回は触っていない

## 気づいたが直さなかったもの

- `style` 属性は手つかず（**2 段目の範囲**）
- `sde.html` の `{% if sde.is_canceled() %}` の繰り返し 6 か所も
  手つかず（**TODO-038 の 1 番目の項目**。依頼書の 1 段目に入って
  いないので触っていない）
- `my.css` の `.my-gage` にある `/* background-color: #FFF; */` は
  コメントアウトされたままだが、依頼書に挙がっていないので残した
- `edit.html` には他にもコメントアウトされた
  `window.addEventListener('resize', …)` のブロックがある。
  こちらは `changeDetailHeight()` を呼ぶもので、生きた関数を指している
  ため残した

## うまくいかなかったところ

特に無し。

## main の判断が要る点

**依頼書が `src/ytsched/webroot/archives/agents/TODO-038/` に置かれている。**
依頼で示されたパス（`/home/ytani/work/ytsched/archives/agents/TODO-038/`）
とは違う。担当の起動時の作業ディレクトリが
`src/ytsched/webroot` なので、相対パスで作られたものと思われる。

`git status` では `?? src/ytsched/webroot/archives/` として残っており、
**このままだと配布物の `webroot` に `archives/` が紛れ込む**。
この報告は依頼どおり `archives/agents/TODO-038/` に置いたので、
依頼書のほうを移す（または消す）かどうかは main が決めてほしい。
main のファイルなので、こちらでは動かしていない。
