# TODO-159 verifier 報告

## lint / test

- `mise run lint` → 全て通過（ruff format/check, eslint, basedpyright, mypy 問題なし）
- `uv run pytest -q` → 607 passed in 159.37s

## chevron-left/right 参照の有無

`grep -rn "chevron-left\|chevron-right" .`（.git 除く）の結果、コードとして
実際に使われる箇所には残っていない（TODO.md 本文と archives の過去記録は
履歴として残るのが自然なので問題なし）。

ただし **`tools/icons_preview.py`** に古い ID が残っている:

```
tools/icons_preview.py:52:    ("chevron-left", "前の週へ / メニューバー"),
tools/icons_preview.py:53:    ("chevron-right", "次の週へ / メニューバー"),
tools/icons_preview.py:172:            ("chevron-left", ""),
tools/icons_preview.py:173:            ("chevron-right", ""),
```

`icons.svg` から `chevron-left` / `chevron-right` の `<symbol>` が削除された
ため、このツールを実行すると存在しない ID を `<use>` で参照するページを
生成することになる（アプリ本体の動作には影響しないが、アイコン確認用
ツールが壊れる）。

## HTML の確認

一時ディレクトリ（`--datadir` 指定）でアプリを起動し、`/` を curl で取得。

- HTTP ステータス: 200
- 取得した HTML 中、該当箇所は次の通り展開されており、`{{ }}` / `{%` の
  生残りなし:
  ```
  ...icons.svg?v=...#triangle-left"></use>
  ...icons.svg?v=...#triangle-right"></use>
  ```
- サーバログに例外・トレースバックなし
- 起動していたプロセスは kill 済み、ポート 18159 の待ち受けは残っていない

## まとめ

- lint / test: 問題なし
- HTML 展開: 問題なし（triangle-left/right が正しく出力されている）
- 見つかった不具合: `tools/icons_preview.py`（52-53, 172-173 行）に
  `chevron-left` / `chevron-right` の参照が残っており、`icons.svg` の
  削除後は存在しない ID を指す。直すかどうかは main の判断。
