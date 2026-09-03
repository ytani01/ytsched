# TODO-177. 編集画面のヘッダーにもフッターと同じボタンを出し、ID 欄を全桁表示する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | implementer + verifier |
| 消費 | output 25,770 / cache_creation 205,563 / 概算 $2.7 |
|      | main 66% + implementer 22% + verifier 12%（料金の割合） |

## きっかけ

編集画面のボタンの帯（戻る・更新・確定・複製・削除）は画面下部にだけ
あった。上下 2 重になっても、編集中に画面のどちらの端からでも押せる
ほうが操作しやすい、という利用者の要望。

ついでに、ID 表示欄が `size="15"` のままで、`sde_id`（UUID 36 文字 +
バージョン番号。TODO-171）が途中で切れていたので広げた。

## やったこと

- ボタン群を `templates/edit_menu.html` へ切り出し、上下 2 か所から
  `{% include %}` する。Tornado の include は呼び出し元の名前空間を
  共有するので、`new_flag` や `date` はそのまま使える
- `edit.html` は `<header>` に `.my-edit-bar-top`、`<footer>` に
  `.my-edit-bar-bottom .my-follow-keyboard` を置いた。**キーボード追従は
  下部だけ**（`keyboard.js` が持ち上げるのは下の帯でよい）
- `my.css` の `.my-edit-bar` から位置指定を外し、`.my-edit-bar-top`
  （`top: 0`）と `.my-edit-bar-bottom`（`bottom: 0`）に分けた。
  上の帯にフォームの先頭が隠れないよう、`.my-edit-main-with-top-bar`
  に `padding-top: 45px` を付けた
- `edit-page.js` の `getElementById("menu")` を
  `querySelectorAll(".my-edit-bar")` へ変え、上下ともリスナーを付ける。
  `id="menu"` は重複するので外した
- ID 欄の `size` を 15 から 45 にした

## テスト

- `tests/test_browser.py` の既存 2 件は、ボタンが上下 2 つに増えて
  Playwright の strict mode に触れるので `.first` を足した。
  DOM 順では上の帯が先なので、この 2 件が押しているのは上のボタン
- 下のボタンにもリスナーが付いていることを見る
  `test_update_button_in_bottom_bar_also_submits` を足した（`.last` を
  押し、ボタンが 2 個あることも確かめる）
- `uv run pytest` は 666 件通過。ruff・型チェックも問題なし
- verifier が playwright で実測した: 上の帯のボタンが実際に効く、
  `sde_id` が全桁見える（`scrollWidth === clientWidth`）、
  上の帯（高さ 45px）にフォーム先頭（y=168px）が隠れない、
  新規では上下とも複製ボタンが出ない、`id` の重複が無い

分担の理由と各担当の報告は
[../agents/TODO-177/README.md](../agents/TODO-177/README.md) にある。
