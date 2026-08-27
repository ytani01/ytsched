# TODO-083 implementer への依頼

`my.js` と `main.html` の JavaScript を分ける。**挙動は変えない。**

## 先に読むこと

- `TODO.md` の TODO-083
- `docs/design-review.md` の I
- `src/ytsched/webroot/static/js/my.js`（1,399 行）
- `src/ytsched/webroot/templates/base.html` / `main.html` / `edit.html`
- `tests/test_browser.py`

## 決まっていること（管理者が決めた。相談は不要）

### 1. 素の `<script>` のまま。ES モジュールにしない

`tests/test_browser.py` が `page.evaluate("days2xPercent(0)")`,
`page.evaluate("DAYS_YEAR")`, `page.evaluate("(d) => pushDateInUrl(d)")`
のように、**グローバルの関数・定数を直に呼んでいる**。テンプレートの
`onmousedown="doGet(...)"` なども同じ。`type="module"` にすると
どちらも壊れるので、**トップレベルの `const`／`let` のまま**にする
（素の `<script>` 同士はグローバルのスコープを共有するので、
ファイルを分けても今までどおり参照できる）。

### 2. ファイルをまたぐ状態は `ytState` にまとめる

`src/ytsched/webroot/static/js/state.js` を新しく作り、次の 5 つを
1 つのオブジェクトに入れる。**全参照を `ytState.xxx` に書き換える**
（約 56 か所）。

```javascript
const ytState = {
    elLoadingSpinner: null,
    elMain: null,
    elGaugeR0: null,
    elWeekWrap: null,
    activeWeekOffset: 0,
};
```

- 元の `let elLoadingSpinner;` などは消す
- 未代入は `undefined` から `null` に変わるが、判定はすべて
  `if ( ! ytState.elGaugeR0 )` のような真偽値なので挙動は変わらない
- **`ytState` に入れるのはこの 5 つだけ。** 1 ファイルの中で閉じている
  状態（`cancelActiveSlide` / `swipeStart` / `swipeDragging` /
  `lastTouchMsec` / `mouseDownEl`）は、そのファイルのトップレベルの
  `let` のまま残す。「このファイル専用」と分かるコメントを添える

### 3. ファイルの分け方

`src/ytsched/webroot/static/js/` に置く。`my.js` は削除する。

| ファイル | 中身（元の my.js の行） |
|---|---|
| `state.js` | `ytState`（新規） |
| `spinner.js` | スピナー（1〜39） |
| `gauge.js` | ゲージ（41〜342） |
| `nav.js` | URL と遷移（344〜696） |
| `week.js` | 週の管理（698〜950） |
| `keyboard.js` | キーボード（952〜1059） |
| `swipe.js` | スワイプとマウス（1061〜1399） |
| `main-page.js` | `main.html` の `<script>` から移す分（新規） |

行番号は目安。**関数・定数の中身は 1 文字も変えない**（`ytState.` を
付ける書き換えだけ）。ファイル冒頭には `/** (c) 2026 ytani01 */` と、
そのファイルが何を持つかの 1〜3 行のコメントを置く。

### 4. `base.html`

`js/my.js` の 1 行を、上の 7 本（`main-page.js` を除く）に差し替える。
`state.js` を先頭に。残りは `spinner` → `gauge` → `nav` → `week` →
`keyboard` → `swipe` の順。

`const url_prefix = '{{url_prefix}}';` のインライン `<script>` は
そのまま残す。

**`main-page.js` は `base.html` に入れない。** 入れると `edit.html` でも
`window.addEventListener('load', onloadHdr)` が走ってしまう。

### 5. `main.html`

`<script>` の中身のうち、**関数本体とリスナー登録を `main-page.js` へ
移す**（`homeButtonHdr` / `onloadHdr` / `changeSearchN` / `clickCount` と、
末尾の `window.addEventListener(...)` 一式）。

`main.html` に残すのは、**テンプレートの値の定数だけ**にして、その直後に
`main-page.js` を読み込む:

```html
<script>
 // main-page.js から使う。テンプレートの値はここでしか取れない
 const search_str0 = '{{ search_str }}';
 const today_str = '{{ today }}';
</script>
<script type="text/javascript"
        src="{{ static_url('js/main-page.js') }}"></script>
```

- `url_prefix` は `base.html` が既にグローバルに置いているので、
  `'{{ url_prefix }}'` は `url_prefix` に置き換える
- `'{{ today }}'` は `today_str` に置き換える
- `homeButtonHdr()` の中の `const search_str0 = '{{ search_str }}';` は
  上へ移したので、関数の中では消す
- `changeSearchN()` の `cur_day.value` は
  `document.getElementById("cur_day").value` に書き換える
  （`window.cur_day` は id 由来のグローバルなので等価。`.js` に移すと
  どこから来た名前か分からなくなるため）
- **エスケープは今と同じにする**（`base.html` の body は
  `{% autoescape None %}`）。`data-*` 属性にはせず、上の `<script>` の
  定数のままにすること

### 6. `edit.html`

`elLoadingSpinner = ...` を `ytState.elLoadingSpinner = ...` に直すだけ。
`edit.html` の `<script>` を外へ出す作業は **この項目では やらない**。

## やってはいけないこと

- 関数の名前を変える、引数を変える、処理を整理する
- `mise run upgradeproject` を走らせる
- テストの内容を変える（`test_browser.py` は 1 行も変えずに通るはず）

## 確かめること

- `mise run test`（または `uv run pytest`）が全部通る
- `mise run lint` / `typecheck` が通る（JavaScript は対象外だが、
  テンプレートを触るので念のため）
- アプリを起動して、週表示が出る。**`--datadir` には必ず一時ディレクトリを
  指定する**

## 報告

`archives/agents/TODO-083/implementer-report.md` に書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。
