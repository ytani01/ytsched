# TODO-038 reviewer 報告

依頼書: `archives/agents/TODO-038/reviewer-request.md`

`git diff` と、1〜3 段目の依頼書・報告（`implementer-request-*.md` /
`implementer-report-*.md` / `main-note-step3.md`）を読んだうえで、
`src/ytsched/webroot` 配下の変更を中身だけ読んで確認した。サーバは
立てていない（画素単位の比較は verifier の担当のため）。

## 見てほしいところへの回答

### 挙動が変わる 2 件

- `edit.html` の `const detail_h` → `let detail_h`。修正されている。
  下限 100 の `if` もそのまま
- `main.html` の `doPost({{ url_prefix }}, …)` と `doPost({{ url }},
  {{ obj }});` は、どちらも第 1 引数に引用符が付いた
  (`doPost('{{ url_prefix }}', …)` / `doPost('{{ url }}', {{ obj }});`)。
  `grep -n "doPost("` で全箇所（7 か所）を洗ったが、引用符の抜けは無い

### 消したものが本当に使われていなかったか

`pagetop.css` / `my_cookie.js` / `MyCookie` / `getBottomDateString()` /
`doGet()` / `editStr()` / `clearBusyFlag()` / `.blinkborder` /
`@keyframes blinkborder` / `.my-osd`（`.my-osd-base` は別物で残っている）
を `src/ytsched/webroot` 全体で grep したが、定義以外の参照は無い。
重複 id（`sde_id` の hidden input・`menu-content`・`<title>`）も、
現状のテンプレートで 1 か所ずつになっていることを確認した。

### CSS のクラス設計

`.my-sde-*` `.my-date-*` `.my-edit-*` は役割 1 つにつき 1 クラスに
なっていて、既存の `.my-bar` `.my-btn` `.my-gage` の命名（`my-` 接頭辞、
ハイフン区切り）に揃っている。`main.html` に残した `.my-fs-*` 10 か所は、
どれもメニューバー・検索欄まわりで役割が 1 か所ずつ違うところで、
依頼書どおり「まとめられないので値の名前のまま」という判断は妥当。

テンプレートで使っている `my-*` クラスと `my.css` で定義している
`.my-*` を突き合わせたところ、食い違うのは `.my-wday-0`〜`6`
（`my-wday-{{ weekday }}` で組み立てるため、静的な grep では出ない）
だけで、他に定義漏れ・参照漏れは無かった。

### 取り消し線 `.my-canceled` と `.my-canceled-items > *`

判断は妥当。`my-canceled` を直接付けているのは、通常予定の時刻欄
（`col-1`）と詳細欄（`col-11 longtext`）で、どちらも `display:
inline-flex` ではないブロックなので、その要素自身に線を引けば足りる。
`my-canceled-items > *` を付けているのは ToDo 行の本文欄（`col-11`）
だけで、ここには `my-sde-sub`（`inline-flex`）・`my-sde-type`・
`my-sde-title`・`my-sde-place` が直接の子として並んでおり、`> *` が
全部を拾えている（漏れている直接の子は無い）。

### `sde.html` の `{{ '\n' + detail + '\n' }}`

意図（`{% if %}` を減らしたことで Tornado の空白の扱いが変わり、
前後の空行がずれるのを式の中で補う）は妥当で、実装もそのとおりになって
いる。テンプレートの地の文に空行を足す書き方より、崩れにくく分かりやすい。

### `.my-bar-content` の `z-index: 100`

コメントどおり。`#menu_bar`（常時表示、`.my-menu-bar` で `z-index:
200`）と、スライドする `.my-bar-content`（`bottom: -60px` で普段は
画面外）はどちらも `.fixed-bottom`（Bootstrap の `z-index: 1030`）が
付いているので、`z-index: 100` が無いと閉じているはずのメニューが
上に出てしまう、という説明で辻褄が合っている。

## 見つけたこと

高い確信度のものは無し。

## 確信度の低い所感（参考）

- **`main.html` の `<script>` 内が全体的に 1 段インデントが浅くなっている**
  （2 段目の報告にもあるとおり 1 段目の変更）。挙動には影響しないが、
  差分が実際の変更点より大きく見える一因になっている
- `.my-canceled`（単数）と `.my-canceled-items`（複数形）で語尾の付け方が
  揃っていないが、動作・可読性には影響しない好みの範囲
- `.claude/agents/implementer.md` / `reviewer.md` の model 変更と
  `TODO.md` の下書きの追記が同じ作業ツリーに混ざっているが、
  `webroot` の変更とは無関係で、TODO-038 の範囲外と判断し確認していない

## 判断が要る点

無し。挙げた 3 点は確認のみで、報告として残すだけ。
