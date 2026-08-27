# TODO-080 verifier 報告

## 1. lint / test

- `mise run lint`（fmt + typecheck）: ○（ruff/ basedpyright/ mypy すべて 0 件）
- `uv run pytest tests`: ○ 465 passed in 47.97s

`DEF_CACHE_SIZE` は実装済みコードで `2000`（main が変更した値）を確認。

## 2. 本題（サーバ動作中の外部書き換えへの追随）

`--datadir` に一時ディレクトリを指定し `--debug` でサーバを起動（port 18765）。

```
curl "http://localhost:18765/ytsched/?date=2026-08-27"   # ORIGINAL を確認
echo '...CHANGED...' > <datadir>/2026/08/27.jsonl        # サーバを止めずに書き換え
curl "http://localhost:18765/ytsched/?date=2026-08-27"   # → CHANGED が返る（○）
```

比較のため `git worktree add <一時dir> HEAD`（TODO-080 の変更をコミット前の
状態、実装は uncommitted のため HEAD＝修正前）で旧コードのサーバを別ポート
（18766）で起動し、同じ手順を行った結果は**古い内容 ORIGINAL のまま**
だった。修正の効果を確認できた（○）。

## 3. ファイルを消したとき

表示させたあとファイルを `rm` して再度取得 → HTTP 200（500 にならない）。○

## 4. 無かった日のファイルをあとから作る

無い日付を先に取得（HTTP 200）→ サーバを止めずに `.jsonl` を新規作成 →
同じ URL を再取得すると新しい内容（`NEWFILE`）が読めた。○

## 5. 書き込み（add/fix/del）と無駄な読み直し

`curl --data "cmd=add&sde_id=&date=...&..."` で `add` を実行（302、
ファイルに書き込まれることを確認）。続けて `fix`、`del` も実行し、
いずれも意図通り動作した（del は `orig_date` を渡す必要があり、
最初 `date` だけで呼んで「消えない」ように見えたのは検証側の
引数指定ミスで、`orig_date` を渡したら正しく削除された。コード側の
不具合ではない）。

`--debug` ログで `cache miss` を数えたところ、`add`/`fix`/`del` の
`save()` 直後には出ておらず、最初にその日付を読み込んだとき
（4 回）以外に発生していない。`save()` 直後の無駄な読み直しは
起きていない。○

## 6. `ytsched migrate` 後、再起動なしで反映（本題の動機）

旧形式 `.cgi`（タブ区切り）ファイルを新規作成し、先に一度その日付を
サーバへ問い合わせて「無い」状態をキャッシュに載せたあと、サーバを
止めずに `uv run ytsched migrate --datadir <同じdatadir>` を実行。
変換後、サーバを再起動せず同じ URL を取得すると、変換された内容
（`MIGRATED`）がそのまま見えた。○

## その他

- サーバのログに例外・トレースバックは出ていない（grep 済み、0 件）
- 見つかった不具合はなし
