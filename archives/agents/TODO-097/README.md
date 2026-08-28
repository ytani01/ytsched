# TODO-097 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |

## なぜこの分担か

`static/js/` の 9 ファイル（`state.js` / `spinner.js` / `gauge.js` /
`nav.js` / `week.js` / `keyboard.js` / `swipe.js` / `main-page.js` /
`edit-page.js`）にまたがり、各ファイルの呼び出し関係を grep で洗い出して
先頭コメントにまとめる。ファイル数が多く、テンプレート（`base.html` /
`main.html` / `edit.html` / `sde.html`）からの参照も追う必要があるので、
実装は `implementer` に分ける。挙動は変えない（コメントの追加だけ）ので、
TODO-017 の基準では `reviewer` は入れない。確認は
`~/.claude/CLAUDE.md` の決まりどおり `verifier` を別に立てる。コメントの
内容の正しさ（外へ出すもの / 外から使うものの向き・帰属・挙げ漏れ）が
この項目の成果物なので、そこを grep で確認させる。

## main が決めたこと

- **コメントは各ファイル冒頭の `/** (c) ... *​/` と `// 〜 (TODO-0xx)` の
  1 行説明の直後に、`//` 行コメントで足す。** 枠線・ASCII アートは使わず、
  既存の `swipe.js` 冒頭（バッククォート無しで名前を並べる）に合わせる。
- **外から使うものに挙げるのは、他 `.js` のトップレベル名と、`base.html` /
  `main.html` の `<script>` 内の定数（`url_prefix` / `search_str0` /
  `today_str` / `auto_turn_msec`）だけ。** DOM 要素の id は全ファイルが
  多数触るので挙げない（主旨がぼやける）。
- **`gauge.js` / `nav.js` / `week.js` は `base.html` であとに読み込む
  ファイルの関数を呼ぶ。** 実行時にしか呼ばれず前方参照でよい、という点を
  該当ファイルのコメントに 1 行添える（この項目の主旨そのもの）。

## main が着手後に直したこと

verifier が挙げた、まとめすぎで実態より広く読める箇所 4 点を main が
直した（コメントのみ）。

- `nav.js`: `shiftDays` / `getLocaltimeString` / `getLocaltimeDateString` /
  `calcDays` を利用元ごとに分けて書いた。`doGet` / `doPost` / `doSubmit` /
  `doGetDate` も、どのテンプレートから呼ばれるかを関数ごとに分けた。
- `gauge.js`: 「外から使うもの（すべて nav.js …）」の見出しが `ytState`
  の行と食い違っていたので、見出しを直し各行に定義元のファイルを付けた。
- `edit-page.js`: `changeDetailHeight()` は自身を `load` に登録して
  いないので、「別の load ハンドラから呼ぶ」に直した。

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [wording-report.md](wording-report.md)
