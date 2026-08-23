# TODO-038 reviewer への依頼

TODO-038（HTML・CSS のリファクタリング）の変更を見てほしい。
**挙動が変わる箇所があるので reviewer を立てた**（`TODO.md` に理由がある）。

## 何が変わったか

作業ツリーに未コミットで入っている（`git diff` と、`git status` の
`D` が付いた 2 ファイル）。3 段階に分けて実装した。

1. [1 段目の依頼](implementer-request-1.md) /
   [報告](implementer-report-1.md)
2. [2 段目の依頼](implementer-request-2.md) /
   [報告](implementer-report-2.md)
3. [3 段目の依頼](implementer-request-3.md) /
   [main の覚書](main-note-step3.md)
   （**3 段目の implementer は落ちたので報告が無い**）

見た目が変わっていないかの確認は verifier が別にやっている。
**こちらは中身を見てほしい。**

## 見てほしいところ

- **挙動が変わる 2 件が正しく直っているか。**
  `edit.html` の `const detail_h` → `let`（横向きで TypeError が出ていた）、
  `main.html` の `doPost({{ url_prefix }}, …)` への引用符の追加
- **消したものが本当に使われていなかったか。**
  `pagetop.css` / `my_cookie.js` の 2 ファイル、`getBottomDateString()`
  `doGet()` `editStr()` `clearBusyFlag()`、`.my-osd` `.blinkborder`、
  重複した id（`sde_id` / `menu-content` / `<title>`）
- **CSS のクラス設計。** 役割で名付けたもの（`.my-sde-*` `.my-date-*`
  `.my-edit-*`）と、値のまま残したもの（`main.html` の `.my-fs-*` 10 か所）
  の分け方が妥当か。名前の付け方が既存（`.my-bar` `.my-btn` `.my-gage`）と
  揃っているか
- **取り消し線の `.my-canceled` と `.my-canceled-items > *` の 2 つ**。
  2 段目の報告に、1 つにまとめられない理由（`<span>` の間の空白に線が入る、
  `inline-flex` に伝わらない）が書いてある。判断が妥当か
- **`sde.html` の `{{ '\n' + detail + '\n' }}`**。テンプレートの改行の数を
  合わせるためのもの。ほかに素直な書き方が無いか
- `.my-bar-content` に足した `z-index: 100`。Bootstrap の `.fixed-bottom`
  （`z-index: 1030`）を打ち消すためのもの
- 見落としているもの、この変更で新しく壊れそうなところ

## 決まりごと

- **コードは直さない。** 見つけたことは報告するだけ。直すかどうかは
  main が決める
- **`TODO.md` は編集しない。git commit もしない**
- サーバを立てる必要があれば **ポート 10095** を使い、`--datadir` には
  一時ディレクトリを指定すること。**ポート 12345 は利用者のもの。止めない**
- 一時ファイルは `/home/ytani/.claude/jobs/795ce790/tmp/` の下に置くこと
- 報告は
  `/home/ytani/work/ytsched/archives/agents/TODO-038/reviewer-report.md`
  に**絶対パスで**書き、返事は 5 行以内で
