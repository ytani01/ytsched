# TODO-209 reviewer 報告

対象: 未コミットの `git diff`（9 ファイル）。コードは直していない。
`src/ytsched/conf.py` は見る点 5 の確認で一時的に書き換え、元に戻した
（`git diff src/ytsched/conf.py` が `"1y"` → `"365"` の 2 行だけであることを確認済み）。

## 確信度の高い指摘

### 1. TODO.md 30〜31 行の前提「base.html にはそのあと式が無いので何も変えていない」は誤り（実装は正しい。記録の直し）

tornado の `{% autoescape %}` は、パースのときに `template.autoescape` を
書き換え（`tornado/template.py` 997 行）、式の出力を生成するときにその値を
見る（同 667 行）。生成はパースが終わってからなので、**ディレクティブより
前にある式も含め、base.html の全体に効いていた**。子テンプレート
（`{% block %}` の中身）は別ファイル扱いで、ずっとエスケープされていた。

実測（`--urlprefix "/a'b"`、`--datadir` は一時ディレクトリ、HEAD の webroot と
作業ツリーの webroot で同じデータを出して比べた）:

| | HEAD（autoescape None あり） | 作業ツリー（削除後） |
|---|---|---|
| `<html data-url-prefix=...>` | `/a'b/` | `/a&#x27;b/` |
| `my.css` の `href` | `/a'b/static/css/my.css?v=…` | `/a&#x27;b/static/css/my.css?v=…` |

つまり削除で、base.html の `url_prefix` / `title` / `version` /
`static_url(...)` がエスケープされるようになった。既定の urlprefix
（`/ytsched`）では出力は空行 1 つを除いて同じ（`_xsrf` 以外の差分なし）。
属性値の実体参照はブラウザが解くので、見た目・動作の実害は無いと見ている
（実害は未確認。特殊文字を含む urlprefix で画面を操作してはいない）。

直すべきは実装ではなく、TODO.md の背景の文（決着時に archives へ移す文）。
新しい `src/README.md` と `docs/data-format.md` の「エスケープされる」は、
この実測と合っている。

### 2. `docs/data-format.md` 386〜390 行の主張は、テンプレートの実測と食い違う（主張の正否は判断しない）

残った文: 「旧形式で画面に見えていた文字列は、`htmlstr2text()` の結果を、
ブラウザが実体参照を 1 回デコードしたもの（ファイルに残っていた `&quot;`
などはブラウザ側で解かれていた）」。

実測（作業ツリーと HEAD で同じ結果）: title に `<b>x</b> &quot; A&B` を入れると

- `/ytsched/`（主画面）: `&lt;b&gt;x&lt;/b&gt; &amp;quot; A&amp;B`
- `/ytsched/edit`: `value="&lt;b&gt;x&lt;/b&gt; &amp;quot; A&amp;B"`
- place `<i>p</i>`、detail `<u>d</u>` も同様に `&lt;…&gt;` になる

ブラウザが 1 回デコードするとテンプレートのエスケープが外れるだけなので、
画面には `&quot;` がそのまま見える。「ファイルに残っていた `&quot;` が
ブラウザ側で解かれていた」は、子テンプレートの式を素直に通した場合とは
合わない。git の履歴では `{% autoescape None %}` は最初のコミット（b54376e）から
base.html にしかなく、`{% raw` は一度も使われていない。

implementer は「因果の説明だけ外し、事実の文は残した」と書いているが、
今のまま読むと理由の無い主張が残っている。旧コードの handler が
テンプレートに渡す前に何かしていた可能性は確かめていない。この主張が誤り
なら、`migrate.py` の `html.unescape()` 2 回のうち 1 回ぶんの根拠が変わる
（53460 項目一致の測り方次第）。**実害は未確認。主張そのものが誤りかどうかは
判断していない。** main の判断が要る。

## 一致したもの

- TODO.md の 5 項目: 差分はすべてを満たし、範囲を超えていない
- `ConfFile.DEF_CONF["ToDo_Days"]` = `"365"`、コメントも一致
- `holiday.fetch()` の `timeout=30`: 一致。タイムアウトの例外は握り潰されず CLI まで上がる
- `sdf_has_sde()` とテスト 3 件の削除: `src/` `tests/` に呼び出しは残っていない。`sdf_exists()` の docstring に消した関数を前提にした文は無い
- `src/README.md` の `load_month_cal()` の説明: `sched_load.py` の実装（`self._sd.get_sdf(date1).sde` を読む）・docstring と一致。以前の「ToDo は反映しない」（TODO-132 以降は誤り）も消えている
- `src/README.md` の CLI 5 つ: `__main__.py` の各コマンドの help と一致（`webapp` の help は "Web server" だけで、README の説明のほうが詳しいが食い違いは無い）
- `src/README.md`「テンプレートの autoescape」の節: 実測と一致
- `docs/data-format.md`「補足」: 実測と一致
- テストの強さ: `DEF_CONF` の `ToDo_Days` を `"1y"` に戻して `uv run pytest tests/test_handler.py -q` → 3 failed / 16 passed（`test_load_conf_no_file`、`test_conf_reloads_when_file_changed_outside`、`test_def_conf_matches_each_class_default`。最後のものは `int('1y')` の `ValueError` で落ちる）。戻したあと元に戻した

### `rg -n 'autoescape|sdf_has_sde|"1y"' --glob '!archives' .` の残り

- 直すべき残り: TODO.md 30〜33 行（上の指摘 1。main が決着時に直す）。ほかには無い
- 残してよい: `main_binder.py:96`（画面の選択肢）、`CLAUDE.md:27`（README の節への案内。節は残っている）、`src/README.md:483,486`（書き直した節）
- 過去のレビュー・提案文書として残してよい: `docs/obsidian-format-review.md` 46・99・213・295 行、`docs/code-review.md` 135・252 行、`docs/web-framework-review.md` 96 行、`docs/image-attach-proposal.md` 254 行。このうち `image-attach-proposal.md:254`（「autoescape None なので今でも書けば表示される」）と `code-review.md:252` は、当時から実測と合わない主張だった

## 確信度の低いもの

- `docs/data-format.md`「補足」と `src/README.md` の「`.html` の出力はエスケープされる」: tornado の既定のエスケープは拡張子によらない。このプロジェクトのテンプレートは全部 `.html` なので誤りではない。言い回しだけの話

## 範囲外で気づいたこと（直していない）

- `src/ytsched/webroot/templates/sde.html:156-159` の HTML コメントの中に `{{ detail }}` があり、tornado が評価するので、予定ごとに detail がコメントの中へもう 1 回出力される（実測で確認）。エスケープされるので `-->` で抜け出すことは無いが、ページが detail の分だけ重くなる
