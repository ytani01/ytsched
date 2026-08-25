# TODO-048 の分担

- 実装: `implementer` — 依頼書 `implementer-request.md`、報告
  `implementer-report.md`。**モデルは定義どおり Sonnet**
- 確認: `verifier` — 依頼書 `verifier-request.md` / `verifier-request-2.md`、
  報告 `verifier-report.md` / `verifier-report-2.md`。**2 回立てた**
- 文書: `wording` — 報告 `wording-report.md`（項目を書き直したとき）と
  `wording-report-2.md`（実施のコミットに入る `.md` 8 つ）

決着は
`archives/todo/TODO-048. Font Awesome をやめて、自作の SVG アイコンにする.md`。

## この分担にした理由

**項目を立てたときに `implementer + verifier` と決めてあった。**
テンプレート 4 つにまたがる置き換えで、実装と確認を分ける基準
（`~/.claude/CLAUDE.md`）にそのまま当たる。

**図案を描くところは main がやった。** アイコン 23 個をどう描くかは
利用者の承認が要る判断で、担当に渡せる形の依頼にならない。確認用の
ページ（`tools/icons_preview.py`）を作ってキャプチャを見せ、承認を
取るまでが main の作業。

**そのぶん、implementer に渡したのは差し替えだけになった。**
どのクラスをどの `<symbol>` の id にするかを対応表にして依頼書へ入れ、
「この表以外の対応を作らないこと」と書いた。判断の要らない作業に
なったので、モデルは定義どおり Sonnet のままで足りている
（料金の割合で 6%）。

**reviewer は入れていない。** 見た目の置き換えで、挙動や分岐は変わらない
と見たため。あとから振り返ると、行の高さの崩れ（下記）は reviewer が
拾える種類のものではなかったので、この判断自体は変えなくてよい。

## verifier を 2 回立てた

1 回目の報告は「崩れなし・指摘なし」だった。そのあと **main が
`getBoundingClientRect()` で数えて、詳細のある行が 44.00px → 50.25px に
太っているのを見つけた**。直したうえで、その直しだけを 2 回目の
verifier に確かめさせている。

**キャプチャを目で見比べる形の確認では、6px の差は出てこない。**
2 回目の依頼書では、旧・新のサーバを別々に立てて同じデータを入れ、
高さを数えて突き合わせるところまで指定した。見た目を変えない類いの
確認では、**依頼書で数えるところまで指定する**。

## `wording` の報告が 2 つある

- `wording-report.md` — TODO-048 の節を「Font Awesome の SVG を使う」案から
  「22 個すべて自作する」案へ**書き直したとき**のもの
- `wording-report-2.md` — **実施のコミット**に入る `.md` 8 つを見たもの。
  「字送りの箱」という言い回しの指摘を受けて、「字面はその枠から
  はみ出して描かれる」に直した
