# TODO-037 verifier への依頼

`TODO.md` の TODO-037 と、
[implementer への依頼](implementer-request.md)・
[implementer の報告](implementer-report.md) を読んでから始めること。

外部 CDN から読んでいた Bootstrap・Font Awesome を同梱し、使っていない
jQuery・popper を消した。**見た目は変えていないはず**というのが実装の
前提なので、そこを疑って確かめてほしい。

## 環境について（先に読むこと）

- **ポート 12345 で、利用者自身が `ytsched` を動かしている。**
  `uv run ytsched webapp -d -p 12345 -u /ytsched2`。
  **絶対に止めないこと。** ポート 12345 も使わない
- 自分が起動するときは **ポート 10097** を使い、`--datadir` には
  一時ディレクトリを指定する（`~/ytsched/data` は実データなので使わない）
- **`uv tool install` はしない。** 今このマシンに `ytsched` はツールとして
  入っていない（`uv tool list` に無い）ので、入れると利用者の環境が変わる。
  同梱したファイルがパッケージに入るかは、下の `uv build` で見る
- `mise run fmt` は走らせない（ファイルを書き換えるため）。
  `mise run lint` / `typecheck` / `test` は叩いてよい

## 確かめること

### 1. 通るか

- `mise run test`（件数を報告に書く）
- `mise run lint`
- `mise run typecheck`

### 2. 外部への通信が残っていないか

一時 datadir でアプリを起動し、`/ytsched/` と `/ytsched/edit` の HTML を
取得して、次の文字列が **1 つも残っていないこと**を確かめる。

```
stackpath.bootstrapcdn.com
use.fontawesome.com
code.jquery.com
cdn.jsdelivr.net
```

`grep -rn` でテンプレート側も見ること（`webroot/templates/`）。

### 3. 同梱したものが実際に配信されるか

起動したサーバから curl で取って、**HTTP 200 と中身の大きさ**を見る。
`base.html` が実際に書いている URL を読んでから叩くこと（パスを推測しない）。

- Bootstrap の CSS
- Font Awesome の `all.css`
- webfont の `.woff2` 2 つ（solid と regular）

`.woff2` が 200 で、かつ**中身がフォントであること**（先頭が `wOF2`）まで
見る。`od -c <ファイル> | head -1` などで。

### 4. Bootstrap が改竄されていないか

同梱した `bootstrap.min.css` から出したハッシュが、元の `base.html` に
書いてあった値と一致すること。

```sh
openssl dgst -sha384 -binary <ファイル> | openssl base64 -A
# 期待値: sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk
# （出力に "sha384-" は付かないので、その後ろと比べる）
git show HEAD~2:src/ytsched/webroot/templates/base.html | grep integrity
```

### 5. パッケージに入るか

`uv build` して、できた wheel の中身に vendor 一式（`.css` と `.woff2`）が
入っていることを確かめる。

```sh
uv build
unzip -l dist/ytsched-*.whl | grep -i -E 'vendor|woff|\.css'
```

**`dist/` は消さずに残すこと**（main が見る）。

### 6. ログ

サーバのログに例外やトレースバックが出ていないこと。404 が出ていないこと
（同梱したファイルのパスが間違っていれば 404 になる）。

## 見た目の比較について

**スクリーンショットの比較は main がやる**ので、ここでは要らない。
HTML の中身と HTTP ステータスまでを見てほしい。

## 決まりごと

- **コードを直さない。** 見つけたことは報告に書く
- **git commit はしない。`TODO.md` は編集しない**
- 報告は `archives/agents/TODO-037/verifier-report.md` に書き、
  返事は 5 行以内で
