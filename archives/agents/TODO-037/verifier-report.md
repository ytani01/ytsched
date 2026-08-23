# TODO-037 verifier 報告

依頼書・`TODO.md` の TODO-037・implementer 報告を読んだうえで、実際に
コマンドを叩いて確かめた。**不具合は見つからなかった。**

## 1. 通るか

```
mise run test
```
`ruff check`: All checks passed!
`basedpyright`: 0 errors, 0 warnings, 0 notes
`mypy`: Success: no issues found in 20 source files
`pytest`: **412 passed**（`mise run test` に lint・typecheck も含まれて実行された）

○ すべて通った。

## 2. 外部への通信が残っていないか

一時 datadir・ポート **10097**（`-u /ytsched`）でサーバを起動し、
`/ytsched/` と `/ytsched/edit?date=2026-08-23` を curl で取得。

```
grep -n -E 'stackpath.bootstrapcdn.com|use.fontawesome.com|code.jquery.com|cdn.jsdelivr.net' index.html edit.html
```
→ **一致無し（exit 1）**。

```
grep -rn -E 'stackpath.bootstrapcdn.com|use.fontawesome.com|code.jquery.com|cdn.jsdelivr.net' src/
```
→ **一致無し（exit 1）**。テンプレート側も含め、ソース全体に残っていない。

取得した HTML に `{{` `{%` の生残りも無い（`grep -n -E '\{\{|\{%' index.html` が
0 件）。

## 3. 同梱物の配信

`base.html` の実際の URL を読んでから叩いた。

| URL | 結果 |
|---|---|
| `/ytsched/static/vendor/bootstrap/bootstrap.min.css` | 200, size=160403 |
| `/ytsched/static/vendor/fontawesome/css/all.css` | 200, size=53741 |
| `/ytsched/static/vendor/fontawesome/webfonts/fa-solid-900.woff2` | 200, size=79072 |
| `/ytsched/static/vendor/fontawesome/webfonts/fa-regular-400.woff2` | 200, size=14868 |

`od -c` で先頭を確認:
- `fa-solid-900.woff2`: `w O F 2 \0 ...` → **wOF2**
- `fa-regular-400.woff2`: `w O F 2 \0 ...` → **wOF2**

いずれもフォント本体であることを確認した。

## 4. Bootstrap の改竄チェック

```
$ openssl dgst -sha384 -binary bootstrap.min.css | openssl base64 -A
9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk

$ git show HEAD~2:src/ytsched/webroot/templates/base.html | grep integrity
integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk"
```
○ **一致した。**

## 5. パッケージに入るか

```
uv build
unzip -l dist/ytsched-*.whl | grep -i -E 'vendor|woff|\.css'
```
vendor 8 ファイル（`bootstrap/LICENSE`, `bootstrap.min.css`,
`fontawesome/LICENSE.txt`, `fontawesome/css/all.css`,
`fontawesome/webfonts/{fa-regular-400,fa-solid-900}.{woff,woff2}`）が
サイズも implementer 報告と一致した状態で入っていた。`dist/` は消さずに
残してある。

（wheel のバージョンは `ytsched-0.3.1.dev2+g1be3c7619.d20260823` で、
アプリ起動時ログの `0.2.1.dev37+g3eb53bf81` と表記が違う。`git describe`
系のタグ設定によるもので、今回の変更とは無関係と判断した。）

## 6. ログ

サーバログ（`webapp.py` / `handler.py` / `main_handler.py` / `edit_handler.py`
の DEBUG 出力）に例外・トレースバックは無かった。「404」の文字列も
0 件。「error」を含む行は `filter_error=False` / `search_error=False` の
デバッグ変数名のみで、実際のエラーではない。

## 環境について

- 利用者のインスタンス（ポート 12345, `/ytsched2`）は触っていない。
  確認後も curl で 200 が返ることを確かめた
- 自分が起動したサーバはポート **10097**、`--datadir` は scratchpad 配下の
  一時ディレクトリ。`~/ytsched/data` には触れていない
- `uv tool install` はしていない
- 確認後、起動したサーバのプロセスは kill 済み（`pgrep -f "10097"` で
  残プロセス無しを確認）

## 判断が要る点

無し。6 項目すべて依頼どおりに通った。見た目の比較は依頼書のとおり
main が行う想定。
