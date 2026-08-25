# TODO-047 の分担

- 実装: `implementer` — 依頼書 `implementer-request.md`、報告
  `implementer-report.md`。**モデルを Opus に上書きした**
- 確認: `verifier` — 依頼書 `verifier-request.md`、報告
  `verifier-report.md`
- レビュー: `reviewer` — 依頼書 `reviewer-request.md`、報告
  `reviewer-report.md`。**モデルを Opus に上書きした**
- 文書: `wording` — 報告 `wording-report.md`。**これは TODO-047 の
  ものではなく、この項目を立てたとき（2026-08-25 06:30）のもの**

決着は `archives/todo/TODO-047. Bootstrap をやめて、素の CSS にする.md`。

## この分担にした理由

**項目を立てたときに、`implementer + verifier + reviewer` と決めてあった。**
3 つのテンプレートにまたがる CSS の書き換えで、`my.css` が 398 → 679 行に
なる規模。実装と確認を分ける基準（`~/.claude/CLAUDE.md`）にそのまま当たる。

**reviewer を入れたのは、挙動の根拠が変わる項目だから。** クラスの見た目は
同じでも、効く理由が「Bootstrap の `!important`」から「`my.css` の中の
並び順」に移る。動くかどうかを見る verifier では、この種の変化は拾えない。
実際に reviewer は、**`.align-middle` が `base.html` の `<link>` の順に
依存するようになったこと**（Font Awesome の `.fa-lg` と同じ詳細度）と、
**`.longtext` の `min-width: 0` が `.row` の直接の子であることに依存する
ようになったこと**を挙げた。どちらもいまは正しく効いていて、テストでも
キャプチャでも出ない。

## モデルを上書きした理由

`implementer` と `reviewer` は、定義ファイルでは `sonnet`。今回は
Agent ツールの `model` で `opus` に上書きした。

CSS の移し替えは、値を写すだけに見えて、実際には reboot の写し漏れ・
ガターの打ち消し・詳細度と並び順・Grid と flex の `min-width` の違いが
からむ。`~/.claude/CLAUDE.md` の「込み入ったロジックの実装、コード
レビューには Opus を充てる」に当たると判断した。

料金の割合は main 60% + implementer 25% + reviewer 12% + verifier 1% で、
確認の担当（verifier）を Sonnet のままにしたぶんは安く済んでいる。

## `wording` の報告が 2 つある

- `wording-report.md` — TODO-047 を**立てたとき**（2026-08-25 06:30）のもの
- `wording-report-2.md` — **決着のコミット**に入る `.md`
  （`archives/todo/TODO-047. ….md`、このディレクトリの依頼書と報告、
  `TODO.md`、`README.md`）を見たもの
