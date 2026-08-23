# TODO-038 implementer への依頼（1 段目・片付け）

`TODO.md` の TODO-038 を読んでから始めること。

TODO-038 は 2 段に分ける。**これは 1 段目で、消すものと直すものだけ。**
`style` 属性を CSS へ寄せる大きい書き換えは 2 段目に回す（見た目が
崩れたときに、どちらのせいか分かるようにするため）。

**見た目を変えないこと。** 例外は 5 番だけ（下に書く）。

## 1. 重複した id を直す

- `sde.html:50-51` の `<input id="sde_id" name="sde_id" type="hidden">` を
  **消す**。1 ページに予定の数だけ同じ id が出ている。`<form>` の外に
  あるので送信されず、JS からも参照されていない
  （`static/js/` と `templates/` を grep 済み）。**消す前に自分でも
  確かめること**
- `main.html:409` と `420` の `id="menu-content"` — 同じ id が 2 つ。
  CSS からも JS からも参照されていないので、**両方とも id を消す**
- `base.html` の `<title>` が 2 回ある（7 行目と 27 行目）。**後ろを消す**

## 2. 使われていない CSS を消す（`static/css/my.css`）

- `.blinkborder` と `@keyframes blinkborder`
- `.my-osd`
- コメントアウトされている `.longtext:focus` のブロック
- 中身が空の `.longtext-sw-label {}`

`.blink` と `@keyframes blink` は**使っている**ので残すこと
（`main.html` と `sde.html` の `class_blink`）。

## 3. 使われていない JS を消す

`static/js/my.js` の次の 3 つ。いずれも定義だけで、呼んでいる箇所が無い
（`templates/` と `static/js/` を grep 済み。自分でも確かめること）。

- `getBottomDateString()`
- `doGet()`
- `editStr()`（`TBD` と書かれている）

`edit.html` の `clearBusyFlag()` も消す（呼び出しがコメントアウトされて
いる）。`busyFlag` 自体は使っているので残すこと。

## 4. どこからも読まれていないファイルを消す

- `static/css/pagetop.css` — `base.html` からも `my.css` からも読み込まれて
  いない。`.pagetop` を使う要素も無い
- `static/js/my_cookie.js` と、`base.html` の `<script>` 1 行 —
  読み込んではいるが、中の `MyCookie` クラスを使っている箇所が無い
  （`new MyCookie` が 0 件）

**どちらも消す前に自分で grep して確かめること。** git に履歴が残るので
戻せる。

## 5. `edit.html` の `const detail_h` を直す（**唯一、挙動が変わるところ**）

`edit.html:98` あたり。

```js
const detail_h = win_h - detail_y - id_h - 7 - 150;
if (detail_h < 100) {
      detail_h = 100;
}
```

`const` に代入しているので、`detail_h < 100` になると
`TypeError: Assignment to constant variable.` で例外になる。実際に
740x360（横向き）で編集画面を開くと出る。`let` にする。

**ここだけは見た目が変わる。** 画面が低いときに詳細欄の高さが 100px に
なる（今は例外で高さの調整そのものが止まっている）。それが本来の意図。

`if` の中の 100 という値も、外の式もそのままにすること。

## 6. `doPost()` の引数に引用符を付ける

`main.html` の 2 か所。

- 100 行目あたり `doPost({{ url_prefix }}, {date: cur_day.value, …})`
- 269 行目あたり `doPost({{ url }}, {{ obj }});`

`{{ url_prefix }}` は `/ytsched/` に展開されるので、いまは
`doPost(/ytsched/, …)` という**正規表現リテラル**が渡っている。文字列に
すると同じ `/ytsched/` になるので偶然動いているだけで、`--urlprefix` に
`[` や `(` が入ると構文エラーになり、日付のボタンが反応しなくなる。

`'{{ url_prefix }}'` のように引用符で囲む（同じファイルの 19 行目・
32 行目が既にその形）。**`{{ obj }}` のほうは Python の dict がそのまま
JS のオブジェクトになっているので、引用符で囲まないこと。** 囲むのは
第 1 引数のパスだけ。

## 確かめること（自分の範囲で）

- `mise run test` が通る
- `mise run lint` が通る
- `--datadir` に**一時ディレクトリ**を指定し、**ポート 10096** で起動して、
  一覧・編集の両方が 200 で返ること（`~/ytsched/data` は使わない）
- **ブラウザの JS で例外が出ていないこと。** 一覧と編集を開いて、
  コンソールにエラーが出ないかを見る。手が無ければ「見ていない」と
  報告に書けばよい（main がスクリーンショットと合わせて見る）

見た目の比較は main がやるので、ここでは要らない。

## 環境の注意

- **ポート 12345 で利用者が `ytsched` を動かしている。止めないこと。**
  ポート 12345 は使わない
- main が 10099、他の担当が 10097 / 10098 を使ったので、**10096** を使う
- `mise run fmt` は走らせてよい（自分の変更を整形するため）。
  `mise run upgradeproject` は走らせない

## 決まりごと

- **`TODO.md` は編集しない。git commit もしない。** main が行う
- 報告は `archives/agents/TODO-038/implementer-report-1.md` に書き、
  返事は 5 行以内で
- 依頼書に無いことを自分の判断で足したら、**足したと分かるように報告に
  書く**
