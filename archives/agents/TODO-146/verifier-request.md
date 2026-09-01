# TODO-146 verifier への依頼

## 目的

TODO-146（CSS のクラス名を役割の名前へ変える）の実装が、**見た目と
挙動を変えずに**できているかを、実装者とは独立に確かめる。
**コードは直さない。** 見つけたことは報告する。

## 前提

- `TODO.md` の「## TODO-146.」の節に、やることと検証の方法がある
- 実装者の報告は `archives/agents/TODO-146/implementer-report.md`
- 変更は `git diff`（`docs/Developer.md` `my.css` テンプレート 4 枚
  `tests/test_web.py` `tools/screenshot.py`）
- 実装者の報告のあと、管理者が次の 4 か所を直している。ここも見ること
  - `main.html:59` の終わりコメントを `<!-- my-week-bar -->` にし、
    `tests/test_web.py:583` の正規表現をそれに合わせた
  - `edit.html:69` の終わりコメントを `<!-- my-edit-bar -->` にした
  - `tools/screenshot.py:70` `DEF_TOGGLE` を `input.my-longtext-sw` に、
    `docs/Developer.md:158` の記述も合わせた

## 確かめること

1. `mise run test`（`fmt` `typecheck` `lint` `test` が走る）。
   **管理者の修正後に走らせ直すこと**（テストとテンプレートを触ったため）
2. テンプレート 7 枚に Bootstrap 由来のクラス名が残っていないこと。
   `class="..."` の中を grep して、`my-` 以外の名前が無いことを確かめる
   （`container-fluid` `row` `col*` `p-*` `m-*` `text-*` `fw-bold`
   `align-*` `border` `d-none` `fixed-*` `alert*`）
3. `my.css` に定義があるのに、どのテンプレートからも使われていない
   クラスが無いこと。逆に、テンプレートで使っているのに `my.css` に
   定義が無いクラスが無いこと（両方向で突き合わせる）
4. 一時ディレクトリを `--datadir` に指定してアプリを起動し
   （実データ `~/ytsched/data` は使わない）、**画面を実際に操作して
   壊れていないこと**を確かめる。少なくとも:
   - 週間表示が出る。上の週バー・ゲージ・下のメニューバーが正しい位置
   - **ハンバーガーメニューの開閉**（`d-none` の `!important` を外した
     ので、いちばん壊れやすい）
   - **予定の詳細の開閉**（`my-longtext-sw`）。開いた本文が折り返し、
     閉じたときは 1 行で省略（`…`）されること
   - 編集画面（新規・既存）。下のボタン帯が中央に並ぶこと
   - ゴミ箱（項目あり・0 件の両方）。チェックボックス、復活、削除
   - 月間表示、ミニカレンダーの表示切り替え
   - 検索、不正な正規表現を入れたときの知らせ（旧 `alert-danger`）
   - 幅 412px と 800px の両方
5. 画面を撮って、目で見ておかしくないことを確かめる
   （`mise run shot`。`DISPLAY` が設定されていると chromium が
   フレームを返さないので `env -u DISPLAY` を通す）
6. ログに例外が出ていないこと

## 報告

`archives/agents/TODO-146/verifier-report.md` に書く。
手順・結果・見つけたこと（無ければ「無し」）・残る懸念。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
