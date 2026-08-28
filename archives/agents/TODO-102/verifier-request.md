# TODO-102 verifier への依頼

## 変更したもの

- `src/ytsched/webroot/static/css/my.css`
  `.my-icon-xl`（1.6em）を新しく足した。`.my-icon-lg`（1.25em）と
  `.my-icon-2x`（2em）の間。
- `src/ytsched/webroot/templates/main.html`
  `<footer>` の中（239〜385 行あたり）の `my-icon-lg` を
  `my-icon-xl` に差し替えた（8 か所）。footer の外（91・94 行）は
  そのまま。

ねらいは、週間表示のフッタのアイコンを、並んでいる入力欄
（検索欄・フィルタ欄、高さ 25.5px）の高さに揃えること。

## 確かめてほしいこと

1. `mise run lint` / `typecheck` / `test` が通るか（`upgradeproject`
   は走らせないこと）
2. ブラウザでフッタのアイコンの高さが 25.5px 前後になっているか。
   `tests/test_browser.py` の起動の仕方を真似て、playwright で
   `#form_search svg`・`#form_filter svg`・`#todo_days_form svg`・
   `#back_button svg`・`#menu_bar label svg` の高さを測る。
   `.my-bar-content` の中は `#menu-sw` をチェックしないと出ない。
   **アプリの起動には `--datadir` に一時ディレクトリを必ず渡すこと**
3. フッタの外のアイコン（週の見出しにある 91・94 行のもの）が
   20px のままか
4. 編集画面（`edit.html`）のアイコンが変わっていないか
5. フッタが 2 段（メニューバーと開くメニュー）とも、アイコンが
   大きくなったことで折り返したり、はみ出したりしていないか。
   幅は 412px で見る

コードは直さないこと。見つけたことは報告に書く。

## 報告

`archives/agents/TODO-102/verifier-report.md` に書く。
返事は 5 行以内で。

## 追加（ホームボタン）

`my.css` に `.my-icon-home`（1.875em）を足し、`main.html` 287 行の
home アイコンを `my-icon-xl` から `my-icon-home` に変えた。隣の日付
表示（`.my-home-date`、30px）と同じ高さにするため。

確かめてほしいこと:

1. `#home_button svg` の高さが 30px、`.my-home-date` と同じか
2. ホームボタンの列（`col-3`）が広がって、隣の検索欄を押し出したり
   折り返したりしていないか（幅 412px）
3. `mise run lint` / `test` が通るか
