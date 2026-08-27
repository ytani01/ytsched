# TODO-083. `my.js` と `main.html` の JavaScript を分ける

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + runner |
| 消費 | output 47,319 / cache_creation 378,502 / 概算 $5.9 |
|      | main 70% + implementer 16% + reviewer 7% + wording 4% + verifier 3% + runner 1%（料金の割合） |

分担の理由と各担当の報告は [`archives/agents/TODO-083/`](../agents/TODO-083/README.md) にある。

## きっかけ

基本設計のレビュー（`docs/design-review.md` の I）で挙がった 2 件。

`my.js` が 1,399 行あり、中身はスピナー / ゲージ / URL と遷移 /
週の管理 / キーボード / スワイプとマウスの 6 つにコメントで分かれて
いた。分かれているのだからファイルも分けられるはずだが、
`elMain` `activeWeekOffset` のような状態がグローバルにあり、
`main.html` の先頭の 120 行の `<script>` から直に書き換えられていた
（`// declared in my.js` というコメントが付いていた）。これが
分けにくくしていた一番の理由だった。

## 着手前に決めたこと

### 1. ES モジュールにはしない

`type="module"` にすると関数と定数がグローバルから消える。だが

- テンプレートのインラインハンドラ（`onmousedown="doGet(...)"` など
  14 か所）
- `tests/test_browser.py` の `page.evaluate("days2xPercent(0)")`、
  `page.evaluate("DAYS_YEAR")`、`page.evaluate("(d) => pushDateInUrl(d)")`

が、どちらもグローバルの名前を直に呼んでいる。どちらも壊れるので、
**素の `<script>` のまま**にした。素の `<script>` 同士は
グローバルのスコープを共有するので、ファイルを分けても今までどおり
参照できる。

### 2. ファイルをまたぐ状態は 1 つのオブジェクトにまとめる

利用者に 3 案を出して選んでもらった。

| 案 | 中身 |
|---|---|
| 要素はその都度取る | 要素をキャッシュするグローバル 4 つを廃止し、`document.getElementById()` を都度呼ぶ |
| **名前空間オブジェクト** | `state.js` に `ytState` を置き、全参照を `ytState.xxx` に書き換える |
| 最小変更 | グローバル変数のまま、ファイル分割と `onloadHdr()` の移動だけ |

**選ばれたのは名前空間オブジェクト。** どこから書き換えられるかを
`ytState` で grep すれば一望できる。

`ytState` に入れたのは、**ファイルをまたぐ 5 つだけ**。

```javascript
const ytState = {
    elLoadingSpinner: null,
    elMain: null,
    elGaugeR0: null,
    elWeekWrap: null,
    activeWeekOffset: 0,
};
```

1 つのファイルの中で閉じている状態（`cancelActiveSlide` は `week.js`、
`swipeStart` / `swipeDragging` / `lastTouchMsec` / `mouseDownEl` は
`swipe.js`）は、そのファイルのトップレベルに `let` で残した。

## やったこと

**挙動は変えていない。**

### 1. `my.js` を 8 本に分けた

| ファイル | 行数 | 元の `my.js` |
|---|---:|---|
| `state.js` | 16 | （新規） |
| `spinner.js` | 34 | 1〜39 |
| `gauge.js` | 308 | 41〜342 |
| `nav.js` | 359 | 344〜696 |
| `week.js` | 255 | 698〜950 |
| `keyboard.js` | 114 | 952〜1059 |
| `swipe.js` | 348 | 1061〜1399 |
| `main-page.js` | 129 | （`main.html` から移した分） |

`ytState` にまとめた 5 つへの参照 58 か所を `ytState.xxx` に
書き換えたほかは、関数・定数の中身に手を付けていない。

### 2. `main.html` の `<script>` を 120 行から 4 行にした

関数本体（`homeButtonHdr` / `onloadHdr` / `changeSearchN`）と、末尾の
`window.addEventListener(...)` 10 行を `main-page.js` へ移した。
`main.html` に残したのは、**テンプレートでしか取れない値の定数 2 つ**
だけ。

```html
<script>
 // main-page.js から使う。テンプレートの値はここでしか取れない
 const search_str0 = '{{ search_str }}';
 const today_str = '{{ today }}';
</script>
<script type="text/javascript"
        src="{{ static_url('js/main-page.js') }}"></script>
```

`data-*` 属性ではなく `<script>` の定数にしたのは、`base.html` の
body が `{% autoescape None %}` で、エスケープの扱いを今までと
同じにするため。

**`main-page.js` は `base.html` に入れていない。** 入れると
`edit.html` でも `window.addEventListener('load', onloadHdr)` が
走ってしまう。`main.html` が自分で読み込む。

### 3. `base.html` と `edit.html`

- `base.html` — `js/my.js` の 1 行を、`state.js` → `spinner.js` →
  `gauge.js` → `nav.js` → `week.js` → `keyboard.js` → `swipe.js` の
  7 本に差し替えた
- `edit.html` — `elLoadingSpinner = ...` を
  `ytState.elLoadingSpinner = ...` に直しただけ。`<script>` を外部
  ファイルへ出す作業は、この項目の範囲外とした

### 4. 文書とコメント

- `src/README.md` に「ブラウザ側のスクリプト」の節を足した
  （8 本の一覧、読み込みの順、`ytState` の線引き）
- `docs/Developer.md` / `tests/README.md` / `tests/test_browser.py` の
  docstring の `my.js` を、`static/js/` の言い方に直した
- `main.html` と `my.css` のコメントに残っていた `my.js` への言及を、
  `swipe.js` / `keyboard.js` に直した（reviewer の指摘）
- `activeWeekOffset` の説明コメントが `state.js` へ移すときに消えて
  いたので戻した（reviewer の指摘）

## テスト

TODO-056 で入れたブラウザのテストで、退行を捕まえられた
（**1 行も変えずに通っている**）。

- `mise run test` — 475 件通過。`tests/test_browser.py` の 19 件も
  skip なし
- `mise run lint` / `typecheck` — 問題なし
- 一時ディレクトリを `--datadir` に指定してアプリを起動し、
  `state.js` 〜 `main-page.js` の **8 本すべてが 200** で返ることと、
  一覧画面・編集画面のどちらもブラウザのコンソールにエラーが
  0 件であることを確認（verifier）
- 元の `my.js` と新しい 7 本を `base.html` と同じ順で結合し、
  `ytState.` を取り除いて `diff` を取った。差分は冒頭のコメントと
  宣言 5 行だけで、**関数・定数の中身は 1 バイトも変わっていない**
  （reviewer）
- `window.addEventListener` の総数が、旧 12 件（`my.js` 2 +
  `main.html` 10）と新 12 件（`main-page.js` 10 + `keyboard.js` 1 +
  `spinner.js` 1）で一致することを確認（reviewer）

## 分かったこと

- **`.js` を 1 本から 8 本に増やす変更は、テストが通っても安心
  できない。** どれか 1 本が 404 になっても、pytest は 1 件も
  落ちないまま画面だけが動かなくなる。
  verifier に「8 本すべてのステータスを見る」と名指しで頼んだのは
  そのため
- **「挙動を変えていない」は、証明の仕方まで頼んで初めて確かめられる。**
  reviewer が結合して `diff` を取る形にしたので、目視では追えない
  1,399 行が 1 バイト単位で確かめられた
