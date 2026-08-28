# TODO-102 verifier 報告

## 1. lint / typecheck / test

- `mise run lint` — 通過（ruff format 31 files unchanged、ruff check All
  checks passed、eslint 問題なし）
- `mise run typecheck` — 通過（basedpyright 0 errors、mypy 28 files 問題なし）
- `mise run test` — 481 passed（tests/test_browser.py の 22 件を含む）

`upgradeproject` は走らせていない。

## 2. フッタのアイコンの高さ（playwright、viewport 412x1600）

`--datadir` に一時ディレクトリを渡してアプリを起動し、chromium で計測。

- `#form_search svg`: height=25.59px
- `#form_filter svg`: height=25.59px
- `#todo_days_form svg`: height=25.59px
- `#back_button svg`: height=25.59px
- `#menu_bar label svg`（`#menu-sw` を checked にして展開）: height=25.59px

いずれも狙い（25.5px 前後、CSS コメントの 1.6em=25.6px）と一致。

## 3. フッタの外のアイコン（91・94 行、週送りの search/circle-up-fill）

`search_mode`（検索フォームを実際に submit）にしないと描画されないため、
`#form_search` から `search_str=a` を送って検索モードにしてから確認した。

- `svg.my-icon-lg` 2 個、height=20px（変わらず）

## 4. edit.html のアイコン

`my-icon-lg` のまま（クラス自体は差し替えていない）。`/edit/` を開いて
確認、`svg.my-icon-lg` が 3 個存在（`.my-icon-lg` の `1.25em` 計算で
22.5px、edit 画面のフォントサイズが違うため main.html の 20px とは
値が異なるが、これは元々の挙動でクラスは変わっていない）。

## 5. フッタの折り返し・はみ出し

viewport 412px で、`#menu_bar` の `getBoundingClientRect().height` と
`scrollHeight` が一致（46px、`overflow: False`）。メニューを開いた
2 段目（`.my-bar-content`）もスクリーンショットで確認し、折り返しや
横方向のはみ出しは無い。

## 判断が要る点

なし。見つかった不具合も無し。

---

## 追加（ホームボタン）確認

- `mise run lint` — 通過（ruff format/check、eslint、basedpyright 0
  errors、mypy 28 files 問題なし）
- `mise run test` — 481 passed
- playwright（viewport 412x1600、`--datadir` に一時ディレクトリ）で計測:
  - `#home_button svg`: height=30px
  - `.my-home-date`: height=30px（一致）
  - `#home_button` 列: width=99px、`#form_search`: x=272.8（押し出されず
    重なりなし）
  - `#menu_bar` の `clientWidth` と `scrollWidth` がともに 412px
    （横方向のはみ出し無し）、`scrollHeight` も `clientHeight` と一致
    （折り返し無し）
  - スクリーンショットでも 1 段目のメニューバーにアイコンの重なり・
    はみ出しは見えない

見つかった不具合なし。
