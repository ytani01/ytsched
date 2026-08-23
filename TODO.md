# TODO

**残っている項目: TODO-037・TODO-038・TODO-039。**
これまでに 36 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-040` から。**

昔（2021 年）に作ったスケジュール管理ソフトを、Python 3.14 / uv / pytest の
環境へ移行する。データディレクトリ `~/ytsched/data` は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にある。既存データは
`ytsched migrate` で一度に変換する。

着手する項目は利用者が指定する。

---

## TODO-037. CDNに依存しないよう同梱する。

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + wording |

- [ ] `jquery` / `popper` / `bootstrap.js` の 3 行を消す（使用箇所ゼロ）
- [ ] Bootstrap 4.5.0 の `bootstrap.min.css` を `static/vendor/` へ置く
      （`base.html` にある `integrity` の sha384 で照合する）
- [ ] Font Awesome 5.6.1 の `all.css` と webfont を `static/vendor/` へ置く
      （`brands` は使っていないので入れない）
- [ ] `base.html` の `<link>` を `static_url()` に差し替える
- [ ] ライセンス表記を置く（Bootstrap は MIT、Font Awesome Free は
      アイコンが CC BY 4.0、フォントが SIL OFL 1.1、コードが MIT）
- [ ] `uv tool install --reinstall .` で webfont まで配信されるか確かめる
- [ ] CDN を遮断した状態で、同梱前と見た目が変わらないことを確かめる

実際に使っているものだけ。外部 CDN が届かないと、レイアウトが崩れて
アイコンが消え、ボタンが押せなくなる。丸ごと同梱にしたのは、見た目を
変えずに依存だけ外すため。使っていないクラスを削るのは TODO-038 の側で
やる。

---

## TODO-038. HTML, CSSの リファクタリング

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer + wording |

- [ ] `sde.html` の `{% if sde.is_canceled() %}` の繰り返し 6 か所を
      class 1 つにまとめる
- [ ] style 属性を CSS へ寄せる
- [ ] 重複した id を直す（`sde_id` / `menu-content` / `<title>`）
- [ ] 使われていない CSS と JS を消す
      （`.my-osd` `.blinkborder` `.longtext:focus` / `editStr()` `clearBusyFlag()`）
- [ ] `edit.html:98` の `const detail_h` 再代入を直す（横向きで TypeError）
- [ ] `main.html:100`・`269` の `doPost({{ url_prefix }}, …)` に引用符を付ける
- [ ] TODO-037 の画面と見比べて、見た目が変わっていないことを確かめる

Python, JavaScriptコードは主眼ではないが、HTML、CSSの修正に際して
コードを修正したほうが良い場合は、修正も可。

reviewer を入れるのは、上の 2 件で挙動が変わるため。テストは本文の語と
`id="date-…"` しか見ておらず、崩れは捕まえない。確かめ方は
スクリーンショットの比較になる。

---

## TODO-039. スマホ用の設定を追加

- manifest.json, apple-touch-iconなど
- favicon.ico も追加
- アイコン画像は、シンプルなものを、独自にデザイン

---

## 完了済み

1 項目 1 ファイル。`archives/todo/` にある（新しい順）。
**やらないと決めたものの理由もそこにある。** 蒸し返す前に読むこと。

- [**TODO-036.** click_utils.py を導入する](archives/todo/TODO-036.%20click_utils.py%20を導入する.md)
- [**TODO-032.** `Conf.cgi` を JSON 形式にする](archives/todo/TODO-032.%20Conf.cgi%20を%20JSON%20形式にする.md)
- [**TODO-031.** 文書に Mermaid の図を入れる](archives/todo/TODO-031.%20文書に%20Mermaid%20の図を入れる.md)
- [**TODO-035.** TODO 項目ごとのトークン消費量を記録する](archives/todo/TODO-035.%20TODO%20項目ごとのトークン消費量を記録する.md)
- [**TODO-034.** `orig_date` と `expanduser()` の紛らわしいところを片付ける](archives/todo/TODO-034.%20orig_date%20と%20expanduser%20の紛らわしいところを片付ける.md)
- [**TODO-029.** コードレビューで見つかった 3 件を直す](archives/todo/TODO-029.%20コードレビューで見つかった%203%20件を直す.md)
- [**TODO-028.** リファクタリングで見つかった残り 5 件を直す](archives/todo/TODO-028.%20リファクタリングで見つかった残り%205%20件を直す.md)
- [**TODO-027.** 不正な入力で 500 になるのをやめる](archives/todo/TODO-027.%20不正な入力で%20500%20になるのをやめる.md)
- [**TODO-033.** URL_PREFIX の改名に追随できていない箇所を直す](archives/todo/TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)
- [**TODO-030.** ドキュメントの役割を分ける](archives/todo/TODO-030.%20ドキュメントの役割を分ける.md)
- [**TODO-023.** mise.toml の見直し](archives/todo/TODO-023.%20mise.toml%20の見直し.md)
- [**TODO-024.** リファクタリングで見つかった 8 件の扱い](archives/todo/TODO-024.%20リファクタリングで見つかった%208%20件の扱い.md)
- [**TODO-026.** 文書の確認の担当と hook を作る](archives/todo/TODO-026.%20文書の確認の担当と%20hook%20を作る.md)
- [**TODO-025.** 文書の確認を分ける仕組みを決める](archives/todo/TODO-025.%20文書の確認を分ける仕組みを決める.md)
- [**TODO-022.** 軽量な担当 runner を作る](archives/todo/TODO-022.%20軽量な担当%20runner%20を作る.md)
- [**TODO-021.** リファクタリング（挙動は変えない）](archives/todo/TODO-021.%20リファクタリング（挙動は変えない）.md)
- [**TODO-020.** JSON Lines への移行ツールと、読み書きの実装](archives/todo/TODO-020.%20JSON%20Lines%20への移行ツールと、読み書きの実装.md)
- [**TODO-019.** 移行元のテストデータを作る](archives/todo/TODO-019.%20移行元のテストデータを作る.md)
- [**TODO-018.** データ形式の見直し（何を変えるかを決める）](archives/todo/TODO-018.%20データ形式の見直し（何を変えるかを決める）.md)
- [**TODO-017.** reviewer の起用基準と、verifier を一律で立てる運用の見直し](archives/todo/TODO-017.%20reviewer%20の起用基準と%20verifier%20の運用.md)
- [**TODO-016.** `date` が空の POST と、存在しない `sde_id` の扱い](archives/todo/TODO-016.%20date%20が空の%20POST%20と、存在しない%20sde_id%20の扱い.md)
- [**TODO-015.** ruff の整形・書き換え系の指摘を解消](archives/todo/TODO-015.%20ruff%20の整形・書き換え系の指摘を解消.md)
- [**TODO-012.** 不正な正規表現を入れられたときの扱い](archives/todo/TODO-012.%20不正な正規表現を入れられたときの扱い.md)
- [**TODO-010.** CLAUDE.md の作成](archives/todo/TODO-010.%20CLAUDE.md%20の作成.md)
- [**TODO-009.** README の更新](archives/todo/TODO-009.%20README%20の更新.md)
- [**TODO-008.** uv tool install 方式へ](archives/todo/TODO-008.%20uv%20tool%20install%20方式へ.md)
- [**TODO-007.** loguru への移行](archives/todo/TODO-007.%20loguru%20への移行.md)
- [**TODO-006.** 型ヒントの整備](archives/todo/TODO-006.%20型ヒントの整備.md)
- [**TODO-004.** lint・型チェックと mise タスク](archives/todo/TODO-004.%20lint・型チェックと%20mise%20タスク.md)
- [**TODO-014.** サブエージェントの報告ファイル名](archives/todo/TODO-014.%20サブエージェントの報告ファイル名.md)
- [**TODO-005.** 明らかなバグの修正](archives/todo/TODO-005.%20明らかなバグの修正.md)
- [**TODO-003.** pytest によるテスト整備](archives/todo/TODO-003.%20pytest%20によるテスト整備.md)
- [**TODO-013.** サブエージェントの常設定義と運用の見直し](archives/todo/TODO-013.%20サブエージェントの常設定義と運用の見直し.md)
- [**TODO-011.** 設定ファイル Conf.cgi の形式（対応しない）](archives/todo/TODO-011.%20設定ファイル%20Conf.cgi%20の形式（対応しない）.md)
- [**TODO-002.** uv プロジェクトへの移行](archives/todo/TODO-002.%20uv%20プロジェクトへの移行.md)
- [**TODO-001.** git リポジトリの初期化](archives/todo/TODO-001.%20git%20リポジトリの初期化.md)
