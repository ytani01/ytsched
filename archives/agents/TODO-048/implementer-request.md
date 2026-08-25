# TODO-048 implementer への依頼: テンプレートを自作アイコンへ差し替える

`TODO.md` の TODO-048 の残り 4 つのチェック項目をやる。図案（`icons.svg`）と
確認用ページは前の作業で済んでいて、図案は承認済み。**今回は差し替えだけ。**

## やること

1. テンプレートの `<i class="fas fa-...">` を `<svg><use>` に置き換える
2. 大きさ（`fa-lg` / `fa-2x` / `fa-9x`）と回転（`fa-spin`）の代わりを
   `my.css` に書く（`.my-spinner` の隣）
3. `base.html` から `all.css` の `<link>` を外し、
   `src/ytsched/webroot/static/vendor/fontawesome/` を消す
   （`git rm -r` を使う。`rm` はエイリアスで止まる）
4. lint・型チェック・テストを通す

## 置き換えの対応表

`src/ytsched/webroot/static/icons/icons.svg` に `<symbol>` が 23 個ある。
FA のクラスと id の対応は次のとおり。**この表以外の対応を作らないこと。**

| いまのクラス | symbol の id |
|---|---|
| `fas fa-home` | `home` |
| `fas fa-search` | `search` |
| `fas fa-bars` | `bars` |
| `fas fa-chevron-left` | `chevron-left` |
| `fas fa-chevron-right` | `chevron-right` |
| `fas fa-angle-down` | `angle-down` |
| `fas fa-filter` | `filter` |
| `fas fa-plus-square` | `plus-square` |
| `fas fa-check-square` | `check-square` |
| `far fa-square` | `square` |
| `fas fa-arrow-alt-circle-up`（solid） | `circle-up-fill` |
| `far fa-arrow-alt-circle-up`（regular） | `circle-up` |
| `far fa-arrow-alt-circle-down` | `circle-down` |
| `far fa-dot-circle` | `dot-circle` |
| `fas fa-arrows-alt-h` | `arrows-h` |
| `fas fa-backspace` | `backspace` |
| `fas fa-trash-alt` | `trash` |
| `fas fa-clone` | `clone` |
| `fas fa-sync` | `sync` |
| `fas fa-spinner` | `spinner` |
| `fas fa-reply` | `reply` |
| `fas fa-exclamation-triangle` | `warning` |
| `fas fa-list-alt` | `list` |

**`solid` と `regular` で字形を分けているのは `arrow-alt-circle-up` だけ**
（`main.html` の solid が `circle-up-fill`、`edit.html` の regular が
`circle-up`）。取り違えないこと。

## 書き方

```html
<svg class="my-icon my-icon-lg align-middle">
  <use href="{{ static_url('icons/icons.svg') }}#home"></use>
</svg>
```

- クラスは `my-icon` が土台で、大きさは `my-icon-lg`（1.25em）/
  `my-icon-2x`（2em）/ `my-icon-9x`（9em）、回転は `my-icon-spin`
- **`fa-lg` などが付いていないものは、大きさのクラスも付けない**
  （`my-icon` だけ。1em）
- **`align-middle` / `align-bottom` はそのまま残す。** 他のクラス
  （`my-btn`、`my-sde-check` など）や `onmousedown` などの属性も、
  付いていたものはそのまま `<svg>` へ移す
- `static_url()` は末尾に `?v=…` を付けるが、`#home` はそのあとに置けば
  効く（`…icons.svg?v=abc#home`）。**実際に絵が出ることを画面で確かめる**

## `my.css` に足すもの

`tools/icons_preview.py` の `CSS` に下書きがある。**そこから
`my-icon*` の部分だけを写し、`.my-spinner` の隣に置く。**

```css
.my-icon {
    width: 1em; height: 1em; vertical-align: -0.125em; overflow: visible;
}
.my-icon-lg   { width: 1.25em; height: 1.25em; }
.my-icon-2x   { width: 2em;    height: 2em; }
.my-icon-9x   { width: 9em;    height: 9em;   stroke-width: 1; }
.my-icon-spin { animation: my-icon-spin 2s linear infinite; }
@keyframes my-icon-spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
```

- 書き方（インデント・1 行 1 宣言）は `my.css` の他の場所に合わせる
- **`my-icon-9x` の `stroke-width: 1` は落とさない。** 9em では太くなりすぎる
- 日本語のコメントを添える。他の場所と同じ調子で

## 消すコメント

Font Awesome が無くなるので、次の記述は**書き直すか消す**。

- `base.html` の 25〜27 行目「my.css は all.css より後に読むこと」
  → 依存が消えるので削除
- `my.css` の 270〜275 行目あたり（同じ話）→ 削除
- `main.html` の 155 行目あたりの `fa-caret-right` / `fa-grip-lines` の
  コメントと、`my.css` の 442〜443 行目の同じ話 → **これは
  ゲージの大きさの由来（TODO-043）なので残す。** 「以前使っていた」と
  過去形で書いてあるので、そのままでよい
- `main.html:120` と `edit.html:162` の、コメントアウトされた
  `<i class="fas fa-sync fa-9x fa-spin"></i>` → **消す**
  （`sync` と `spinner` は別のままにすると決めたので、この覚書は要らない）
- `my.css` の `.my-sde-check`（`font-size: small`）は、
  `<i>` から `<svg>` になると効き方が変わる。**大きさが変わっていないか
  画面で確かめ、必要なら直す**（直したら報告に書く）

## 確かめ方

1. `mise run lint` と `uv run pytest tests`
   （テンプレートを触るのでゴールデンマスターテストが落ちるはず。
   落ちたら中身を見て、意図した変化かどうかを報告に書く。
   **期待値を書き換えてよいかは main が決める**ので、勝手に直さない）
2. アプリを起動して画面を見る。**架空のデータを用意してある**ので、
   そのまま使ってよい（実データは汚さないこと）

   ```sh
   uv run ytsched webapp \
     --datadir /tmp/claude-649/-home-ytani-work-ytsched/a2bb2f43-efc3-49b3-b5f9-66676d2024ec/scratchpad/data \
     --port 10089
   ```

   URL は `http://localhost:10089/ytsched/`
3. キャプチャ。**`env -u DISPLAY` を付ける**（この環境の癖。TODO-051）

   ```sh
   env -u DISPLAY uv run --with playwright python tools/screenshot.py \
     'http://localhost:10089/ytsched/' -p todo048-impl --open
   ```

   **変更前のものは `todo048-before-*` という名前で main が撮ってある。
   消さないこと。** 自分が撮るものは `todo048-impl-*` にする。
   撮ってあるのは次の 6 通り（幅 412px と 800px の 2 枚ずつ）。

   | 名前 | URL / 状態 |
   |---|---|
   | `todo048-before-main_closed` | 一覧 |
   | `todo048-before-main_open` | 一覧、詳細を開いた状態（`input.longtext-sw`） |
   | `todo048-before-menu_open` | 一覧、メニューを開いた状態（`--toggle '#menu-sw'`） |
   | `todo048-before-edit_closed` | 編集画面（既存の予定）`/edit?date=2026-08-25&sde_id=id-0006` |
   | `todo048-before-editnew_closed` | 編集画面（新規）`/edit?date=2026-08-27` |

   **字形は別物になるので、画素で一致するかは見ない。** 見るのは
   **大きさ・縦位置・行の詰まり具合が崩れていないか**の 1 点。
   ずれていたら、`my.css` の `vertical-align` などで合わせる
4. **読み込み中のしるし（`spinner` + `my-icon-spin`）はキャプチャに写らない。**
   `page.evaluate()` で `#loadingSpinner` の `display` を出したうえで撮るなど、
   別に確かめること
5. `grep -rn 'fa-\|fas \|far \|fontawesome' src/` で、消し残しが無いこと

## 報告

`archives/agents/TODO-048/implementer-report.md` に書く。**返事は 5 行以内**で、
終わったか・報告ファイルのパス・判断が要る点だけ。ファイルの全文は貼らない。

報告に必ず入れること:

- 置き換えた箇所の一覧（ファイルと行）
- `my.css` に足したもの
- テストの結果（落ちたものがあれば、その中身と、意図した変化かどうかの見立て）
- 変更の前後のキャプチャを見比べて、**崩れていないと判断した根拠**
- `.my-sde-check` を直したかどうか
- 迷ったところ、main に決めてほしいこと
