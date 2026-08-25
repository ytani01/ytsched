# TODO-053. キャプチャで、404 のページを黙って撮ってしまうのを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier |
| 実施 | Sonnet 5 / effort medium | main のみ + verifier |
| 消費 | output 10,302 / cache_creation 112,174 / 概算 $1.3 |
|      | main 88% + verifier 12%（料金の割合） |

依頼と報告は `archives/agents/TODO-053/` にある。

## きっかけ

TODO-051 で `DEF_URL` を直したとき、verifier が気づいた。
`page.goto()` の戻り値を見ていないので、404 のページでもそのまま
PNG を保存してしまう。旧既定の `http://localhost:10085/edit/` で実際に
起き、404 のページが写った 4.6KB の PNG ができた。

URL を間違えたことに気づけないと、TODO-048・TODO-049 のような
変更の前後を突き合わせるキャプチャで、どちらも 404 のページだと
「変わっていない」と読めてしまう。

## やったこと

`tools/screenshot.py` に `HttpError` 例外クラスを足した。`shoot()` 内で
`page.goto()` の戻り値（`Response`）の `status` を見て、200 以外なら
撮らずに `HttpError(status, url)` を投げる。`main()` 側でこの例外を
捕まえ、`{status}: {url}` と `URL を確かめる。` を標準エラーに出して
終了コード 1 で終える。

```
$ mise run shot -- http://localhost:10085/edit/
404: http://localhost:10085/edit/
URL を確かめる。
$ echo $?
1
```

既存の `except Exception` にまとめる案もあったが、そこに出るメッセージ
（`アプリが {url} で動いているか確かめる。`）は URL 間違いの場合と
意味が違うので、`HttpError` 専用の分岐を分けて `URL を確かめる。` を
出すことにした。

`docs/Developer.md` の「画面を撮る」の節に、この挙動と実行例を足した。

## テスト

verifier に確認させた（`archives/agents/TODO-053/verifier-report.md`）。

- 一時ディレクトリを `--datadir` に指定してアプリを起動
- 200 の URL（`http://localhost:10085/ytsched/`）では今までどおり
  PNG が撮れること
- 404 の URL（`http://localhost:10085/edit/`）では PNG が
  できていないこと
- 404 のときの標準エラーが `404: <url>` / `URL を確かめる。` の
  2 行で、終了コードが 1 になること
- `uv run pytest tests` … 427 件通過
- `uv run ruff format` / `ruff check` / `basedpyright` … 問題なし

不具合は見つからなかった。
