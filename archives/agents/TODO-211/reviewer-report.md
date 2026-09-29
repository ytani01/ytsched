# TODO-211 reviewer 報告

対象: `git diff docs/data-format.md`（未コミット）。コードと文書は直していない。

## 結論

確信度の高い食い違いは **無し**。主張 1〜4 は実測と一致した。
確信度の低い指摘を 2 つ、後ろに置く。

## 測った値

### (a) `render_old.py`（tornado 6.5.10）

stderr に `stub date` `date_from` `date_to` `search_str`（未使用の名前を空で埋めたもの）。該当行:

```
88: <span style="font-size: medium; font-weight: normal">T &amp;quot;a&amp;quot; &amp;amp; &lt;b&gt;x&lt;/b&gt;</span>
91: @X&amp;quot;Y &lt;i&gt;p&lt;/i&gt;
109: style="font-size: x-small;">D &amp;quot;q&amp;quot; &amp;lt;u&amp;gt;
110: line2</div>
```

- 主張 1: 一致。`base.html` を継承した子テンプレートのブロックでも、`include` した `sde.html` でもエスケープされる。
  tornado の `_NamedBlock.generate` と `_IncludeBlock` は `writer.include(<そのテンプレート>)` で
  `current_template` を切り替え、`_Expression` はその `autoescape` を見る（`tornado/template.py` 559, 667 行）。
  旧 `main.html:295` の `{% include sde.html %}`（引用符なし）は、`render_old.py` の `"sde.html"` と同じに
  扱われる（985 行で引用符を剥がす）
- 主張 3: 一致（`&quot;` → `&amp;quot;`。ブラウザには `&quot;` と出る）
- 主張 4: 一致（`<b>` `<i>` が `&lt;b&gt;` などになる）

### (b) 旧 `htmlstr2text()`（`c4e31b4:ytsched/ytsched.py` 1〜53 行から `my_logger` の import を除いて取り出したもの）

| 入力 | 出力 |
|---|---|
| `&quot;` | `&quot;`（そのまま） |
| `&amp;` | `&amp;`（そのまま） |
| `&lt;` | `<` |
| `&gt;` | `>` |
| `&nbsp;` | ` `（半角空白） |
| `&#160;` | ` ` |
| `&amp;#160;` | ` ` |
| `&amp;#12316;` | `&amp;#12316;`（そのまま） |
| `<BR>` | `\n` |
| （参考）`<br />` | `\n` |
| （参考）`（全角）` | `(全角)` |
| （参考）`&nbsp:` | ` `（コロンの打ち間違いも拾う） |

主張 2: 一致（解く実体参照は `&lt;` `&gt;` `&nbsp;` `&#160;` `&amp;#160;` だけで、`&amp;` → `&` の行はコメントアウト）。

### (c) `htmlstr2text(値)` を title に入れて旧テンプレートで描画（`[` `]` で挟んだ）

| 入力 | `htmlstr2text` | 出力 HTML |
|---|---|---|
| `&quot;` | `&quot;` | `[&amp;quot;]` |
| `&amp;` | `&amp;` | `[&amp;amp;]` |
| `&lt;` | `<` | `[&lt;]` |
| `&gt;` | `>` | `[&gt;]` |
| `&nbsp;` | ` ` | `[ ]` |
| `&#160;` | ` ` | `[ ]` |
| `&amp;#160;` | ` ` | `[ ]` |
| `&amp;#12316;` | `&amp;#12316;` | `[&amp;amp;#12316;]` |
| `<BR>` | `\n` | `[\n]` |

予想どおり（`&amp;#160;` は空白、`&amp;#12316;` は `&amp;amp;#12316;`）。

使ったスクリプトはスクラッチパッドに置いた（コミット対象外）。

### (e) 他の現行文書

- `src/README.md:483-486`: 一致（いまのテンプレートはエスケープされ、`base.html` にも `autoescape None` は無い、と書いてある）
- `CLAUDE.md:27`: 節の名前だけなので問題なし
- 過去の文書に誤りがあるだけ: `docs/obsidian-format-review.md:213`（「`base.html` は `autoescape None` のまま」だからアプリ側の見え方は変わらない）、
  `docs/image-attach-proposal.md:254`（「`{% autoescape None %}` なので書けば表示される」）、
  `docs/code-review.md:252`

### (f) 前後との食い違い

- 基準の書き方 `html.unescape(htmlstr2text(ファイルの値))`: `archives/agents/TODO-018/verifier-report-2.md` 81〜83 行の
  「旧の画面」= `html.unescape(htmlstr2text(生の値))` と一致。`detail` に `htmlstr2text()` が 2 回掛かる件は、同報告 93〜97 行で
  結果の差 0 件と確かめてあり、数字に影響しない
- 手順 5（`&amp;#160;` を旧コードも直していた、`<br />` 以外のタグは文字のまま出る）: 一致
- 手順 6、168 項目の表: 基準に対する差としては一致。`&amp;#12316;` の行は、基準では `&#12316;`、移行後は `〜` なので差に数えられている（(b) で `html.unescape` 後が `&#12316;` になることを確かめた）
- 同報告 89〜92 行の「旧の画面 = ブラウザが実体参照を 1 回デコードしたもの という前提は妥当」は、(a) で誤りと分かった。`archives/` なので直す対象ではない（参考のみ）

## 確信度の低い指摘

1. **`docs/data-format.md` 396〜397 行: `htmlstr2text()` の説明に全角括弧の半角化が無い。**
   「解くのは … だけ」は実体参照とタグの話としては正しい。ただ、この節の題は「画面の見え方はどう変わるか」で、
   旧画面は `（）` を `()` にして出していたため、全角括弧を含む項目も移行後に見え方が変わる（下の表の 157 項目）。
   本文は「実体参照の残っている項目は … 見え方が変わる」としか言っておらず、括弧のほうは表で初めて出てくる。
   手順 5 に「全角括弧の半角化まで一緒にやってしまう」とあるので、読めば分かる。実害は未確認
   （漏れと見るか、表で足りていると見るかは main の判断）
2. **tornado の版。** 測ったのは 6.5.10。旧アプリは `setup.cfg` で `tornado` を版の指定なしで入れていたので、
   当時の版は分からない。`include` と継承したブロックがそれぞれのテンプレートの `autoescape` を使う作りは
   古くからあると見ているが、当時の版で測ってはいない。実害は未確認
