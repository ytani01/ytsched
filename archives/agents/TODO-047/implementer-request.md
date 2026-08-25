# TODO-047 implementer への依頼

`TODO.md` の TODO-047「Bootstrap をやめて、素の CSS にする」を実装する。
項目の本文を先に読むこと。

## 決まっていること（利用者が決めた。相談しなおさない）

1. **クラス名は変えない。** `row` `col-1`〜`col-11` `col` `p-0` `p-1`
   `p-2` `m-0` `m-1` `text-center` `text-start` `text-end` `fw-bold`
   `align-middle` `align-bottom` `d-none` `border` `fixed-bottom`
   `container-fluid` `alert` `alert-danger` は、**同じ名前のまま
   `my.css` に定義する**。テンプレートの `class="..."` は原則さわらない
   （下の「テンプレートを触ってよい場合」だけ例外）
2. **`scroll-behavior` の件は今回やらない。** Bootstrap の
   `:root { scroll-behavior: smooth }` は無くなるが、`my.js` の
   `"instant"`（TODO-041 の回避）と `main.html` のコメントは**そのまま
   残す**。動きは変わらない
3. **Font Awesome は触らない**（TODO-048 の範囲）

## やること

### 1. `my.css` に Bootstrap の代わりを書く

置き換えが要るものは、テンプレート 4 つ
（`base.html` `main.html` `edit.html` `sde.html`）で実際に使っている
次のクラスだけ。**これで全部**（`class="..."` を機械的に集めたもの＋
テンプレート変数経由で入る `fw-bold` を足した）。

| 種類 | クラス |
|------|--------|
| レイアウト | `container-fluid` `row` `col` `col-1` `col-2` `col-3` `col-4` `col-5` `col-6` `col-9` `col-10` `col-11` |
| 余白 | `p-0` `p-1` `p-2` `m-0` `m-1` |
| 文字 | `text-center` `text-start` `text-end` `fw-bold` |
| 縦位置 | `align-middle` `align-bottom` |
| その他 | `d-none` `border` `fixed-bottom` `alert` `alert-danger` |

`fw-bold` はテンプレートの変数から入る（`main.html` の `class_today`、
`sde.html` の `class_important`）ので、`class="..."` を grep しても
出てこない。忘れないこと。

**元の値は `static/vendor/bootstrap/bootstrap.min.css`（v5.3.8）から
そのまま読み取ること。**推測で書かない。消す前に読む。

### 2. `row` / `col-N` は CSS Grid にする

Bootstrap では flexbox（`.row{display:flex;flex-wrap:wrap}` ＋
`.col-N{width:8.33…%}`）だが、**CSS Grid（12 列）に置き換える**。
テンプレートを確かめたところ、どの `row` も子の合計がちょうど 12 列に
なっていて折り返しは起きていないので、Grid に移して見た目は変わらない。

- `col`（数字なし）は `edit.html` で必ず 1 行に 1 つだけ使われている。
  12 列ぶんに広がればよい
- **`min-width: 0` は `.row > *` にまとめてかける。** Grid の子も
  flex と同じで既定が `min-width: auto` なので縮まない（TODO-045）。
  まとめてかけたら、`.longtext` と
  `.longtext-sw:checked ~ .longtext` の個別の `min-width: 0` は消す。
  そのとき TODO-045 のコメントも書き直すこと（「Bootstrap の
  `col-11` に任せる」という説明が合わなくなる）

**ガター（溝）を落とさないこと。** Bootstrap は
`--bs-gutter-x: 1.5rem` で、`.row` に左右 `-12px` のマージン、
`.row > *` と `.container-fluid` に左右 `12px` のパディングを入れている。
`p-0` `p-1` `p-2` `m-0` `m-1` はこれを打ち消すためのもの。
**`m-*` が付いていない `row` が `edit.html` に 4 つある**（`p-1
my-edit-row` の行、`my-edit-row` の行、`div_detail`、`div_id`）ので、
ここは負のマージンが効いている。落とすと編集画面の横幅が変わる。

### 3. Bootstrap の reboot（土台の指定）を写す

**ここがいちばん抜けやすい。** `bootstrap.min.css` は
normalize / reboot を含んでいて、これが無くなると 4 つのクラスを
そろえても見た目が変わる。テンプレートで実際に使っている要素に
かかるものを、`bootstrap.min.css` から拾って `my.css` に写すこと。
少なくとも次は関係する（他にもないか自分で確かめる）。

- `*,::after,::before{box-sizing:border-box}`
- `body` の `margin:0` / `font-family` / `font-size` / `font-weight` /
  `line-height` / `color` / `background-color` /
  `-webkit-text-size-adjust` / `-webkit-tap-highlight-color`。
  **`color` は `#212529` で、黒ではない**
- `button,input,optgroup,select,textarea{margin:0;font-family:inherit;
  font-size:inherit;line-height:inherit}` … `<input type="date">`
  `<input type="time">` `<select>` `<textarea>` の見え方が変わる
- `::-webkit-datetime-edit-*{padding:0}` など、日付・時刻の入力欄まわり
- `img,svg{vertical-align:middle}` … ゲージの SVG に効いている
- `label{display:inline-block}` … メニューの開閉ラベル
- `strong` の指定

`my.css` の先頭にある `--bs-body-font-family`（TODO-040）は、
Bootstrap が無くなるので変数名ごと見直す。**あの値でなければ行の高さが
変わるという事情（TODO-040）は変わらない**ので、値と理由のコメントは
残すこと。

**写した値の出どころを `my.css` のコメントに書く**
（「Bootstrap 5.3.8（MIT, Copyright (c) 2011-2025 The Bootstrap
Authors）から値を写した」程度）。`static/vendor/bootstrap/LICENSE` は
ディレクトリごと消えるので、告知はこのコメントに残す。

### 4. `!important` を減らす

`my.css` にいまある 5 か所の `!important`
（`.my-btn:active` `.my-date-block` `.my-date-block-today`
`.my-canceled` `.my-canceled-items > *`）は、Bootstrap のユーティリティ
（`.border` など）に勝つためのもの。

**`my.css` の中の並び順で解けるようにする。** 上で足すユーティリティ
（`.border` `.p-*` `.m-*` `.text-*` など）を `my-*` の各クラスより
**前**に置けば、詳細度が同じなので後ろの `my-*` が勝つ。
そのうえで `!important` を外し、**外しても見た目が変わらないことを
自分で確かめる**。外せないものがあれば、残した理由を報告に書く。

`.d-none` だけは `!important` を残してよい（要素を隠す指定なので、
後ろの `my-*` に負けると困る）。判断は任せる。報告に書くこと。

### 5. `base.html` から読み込みを外し、`vendor/bootstrap/` を消す

- `base.html` の `bootstrap.min.css` の `<link>` を消す。
  Font Awesome の `<link>` は残す
- `git rm -r src/ytsched/webroot/static/vendor/bootstrap` で消す
  （`\rm` ではなく `git rm`）
- `my.css` の `.my-bar-content` のコメントが
  「`.fixed-bottom (bootstrap)` の z-index: 1030 を打ち消す」と
  書いてあるので、実情に合わせて直す
- ほかに Bootstrap を指している記述が残っていないか、
  `grep -rn -i bootstrap src docs tests README.md` で確かめる。
  `docs/` や `README.md` に説明があれば直す（`archives/` は直さない）

## テンプレートを触ってよい場合

原則さわらないが、次は例外として認める。**やったら報告に書くこと。**

- `align-middle` / `align-bottom` は `vertical-align` であって、
  Grid の `align-self` とは別物。テンプレートごとに「どちらの意味で
  使っているか」を見て、`vertical-align` のままでよいか確かめる。
  意味が変わってしまう箇所があれば、CSS 側で吸収できないか先に考え、
  それでも駄目ならテンプレートを直してよい
- Grid にしたことで、いまのマークアップのままでは同じ見た目にできない
  箇所（あれば）

## 確かめ方

見た目を変えないための項目なので、テストでは確かめられない。

1. `mise run lint` と `uv run pytest tests`（テンプレートを触るので
   ゴールデンマスターテストが落ちる可能性がある。落ちたら中身を見て、
   意図した変化かどうかを報告に書く。**期待値を書き換えてよいかは
   main が決める**ので、勝手に直さない）
2. アプリを起動して画面を見る。**`--datadir` に一時ディレクトリを
   指定すること。** 架空のデータを
   `/tmp/claude-649/-home-ytani-work-ytsched/6d4b41c4-d525-49f9-b349-30a9b032fdc2/scratchpad/data`
   に用意してある（2026-08-25 を今日として作ってある）。そのまま使ってよい

   ```
   uv run ytsched webapp --datadir <上のパス> --port 10088
   ```

   URL は `/ytsched/` 配下。`http://localhost:10088/ytsched/`
3. キャプチャ。**`DISPLAY` が設定されていると chromium がフレームを
   返さず `Page.screenshot` がタイムアウトする**ので、`env -u DISPLAY`
   を付ける（この環境の癖。`tools/screenshot.py` はまだ対応していない）

   ```
   env -u DISPLAY uv run --with playwright python tools/screenshot.py \
     'http://localhost:10088/ytsched/' -p todo047-impl --open
   ```

   撮ったものは `~/tmp/playwright-mcp/` に入る。**変更前のものは
   `todo047-before-*` という名前で main が撮ってあるので、消さないこと。**
   自分が撮るものは `todo047-impl-*` のように別の名前にする

   変更前に撮ってあるのは次の 5 通り（幅 412px と 800px の 2 枚ずつ）。
   同じところを撮って見比べること。

   | 名前 | URL / 状態 |
   |------|-----------|
   | `todo047-before-main_{closed,open}_{412,800}` | `/ytsched/`。`open` は詳細を開いた状態 |
   | `todo047-before-menu_{closed,open}_{412,800}` | `/ytsched/`。`open` はメニュー（`#menu-sw`）を開いた状態 |
   | `todo047-before-edit_closed_{412,800}` | `/ytsched/edit/?date=2026-08-25&sde_id=id-0006` |
   | `todo047-before-alert_closed_{412,800}` | `/ytsched/?search_str=%5B`（正規表現が不正 → `alert-danger` が出る） |
   | `todo047-before-search_closed_{412,800}` | `/ytsched/?search_str=%E4%BC%9A%E8%AD%B0`（検索モード。`col-2`/`col-10` の行が出る） |

   メニューを開いた状態は `--toggle '#menu-sw' --open` で撮れる。
   編集画面・alert・search は `--open` 無しでよい

**最終的な確認は verifier が別に行う**が、自分でも上を一通り走らせて、
結果を報告に書くこと。

## 報告

`archives/agents/TODO-047/implementer-report.md` に書く。返事は 5 行以内。
とくに次を落とさないこと。

- `!important` を外せたもの・残したものと、その理由
- テンプレートを触ったなら、どこを・なぜ
- 変更前と見比べて**違いが出た箇所**（無ければ「無し」と書く）
- ゴールデンマスターテストが落ちたなら、どのテストが・どう変わったか
