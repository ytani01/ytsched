# TODO-088 verifier 報告

## 1. いつもの確認

- `uv run pytest -q` → 475 passed（見込み通り）
- `mise run lint`（fmt/ruff/basedpyright/mypy）→ すべて通過

## 2. 変更の前後で HTML が同じか（本命）

`git worktree add /tmp/.../ytsched-old HEAD`（TODO-087 時点）で変更前を
取り出し、同じ合成データ（予定 17 件・ToDo 4 件、うち「findme」を含む
語を近い日付と ±900 日離れた日にも配置）を 2 つのデータディレクトリに
複製して、ポート 18801（旧）・18802（新）で起動して突き合わせた。

- `GET /ytsched/?date=` 平日(2026-08-28) / 日曜(2026-08-30) / 月曜(2026-08-24)
  → 一致（`<title>` の版数のみ差分。無視してよい範囲）
- 検索 `search_str=findme` × `search_n=1/5/100` → 一致
- 検索 `search_str=zzznohitzzz`（当たらない語）→ 一致
- `todo_days=-1` / `todo_days=365` → 一致
- `filter_str=findme` / `filter_str=!findme` → 一致
- `data-monday`/`data-offset` の出方 → 通常モードで 9 件ずつ、検索モードで
  0 件、旧・新とも同じ
- 数百日離れた一致（±900 日）は `search_n=1000` でも旧・新とも拾わない
  （365 日で打ち切る仕様どおりで、旧・新の挙動は一致）

**差は見つからなかった。**

途中、自分のテストデータ作成の手順ミス（`data-new` を先に `mkdir` して
いたため `cp -r data-old data-new` が `data-new/data-old/` に潜り込み、
新側のデータディレクトリが空扱いになっていた）で「一覧が全部空になる」
という偽の差分が一度出た。作り直して解消。実装のバグではない。

## 3. サーバのログ

`old.log` / `new.log` に `error` `traceback` `exception`（大小文字問わず）
は無し。

## 後片付け

`git worktree remove` 済み。サーバプロセスは PID を確認して kill 済み。
