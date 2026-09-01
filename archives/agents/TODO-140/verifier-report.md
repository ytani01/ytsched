# TODO-140 verifier 報告

## 結果

○ 依頼された確認はすべて成功した。不具合は見つからなかった。

## 1. テスト一式

実行コマンド:

```sh
mise run test
```

結果:

- ○ formatter: Ruff は 38 files left unchanged、Prettier は全 11 JS が unchanged。
- ○ Ruff check: All checks passed。
- ○ basedpyright: 0 errors, 0 warnings, 0 notes。
- ○ mypy: 35 source files、Success: no issues found。
- ○ ESLint: 成功。
- ○ pytest: 581 passed in 146.80s。
- ○ `mise run test` 全体: Finished in 154.06s。

## 2. 一時 datadir での HTML 確認

実データは使用していない。`mktemp -d` で作った
`/tmp/todo140-data.EKU6AA` に 2 件だけの `trash.jsonl` を置いた。

実行コマンド:

```sh
mise run webapp -- --datadir /tmp/todo140-data.EKU6AA --port 10140
curl http://127.0.0.1:10140/ytsched/trash
curl 'http://127.0.0.1:10140/ytsched/trash?sde_id=id-1'
curl http://127.0.0.1:10140/ytsched/trash
```

- ○ 起動と HTML 取得: 通常・`sde_id=id-1`・空の全て HTTP 200。
- ○ 通常（2件）: header 内の clear form は 1 個、main 内は 0 個。
- ○ 通常（2件）: header に「ゴミ箱」と「2件」、`aria-label="空にする"`、
  `#trash` を各 1 個確認。
- ○ 通常（2件）: `my-trash-clear-row` は HTML に 0 個。
- ○ 絞り込み: clear form は 0 個。
- ○ 空: clear form は 0 個、「0件」は 1 個。
- ○ `trash.html` と `my.css`: `my-trash-clear-row` の検索結果は 0 件。

## 3. clear の HTTP 動作

2 件のデータを再投入して、次を実行した。

```sh
curl -D clear.headers -o /dev/null -X POST -d 'cmd=clear' \
  http://127.0.0.1:10140/ytsched/trash
```

- ○ HTTP ステータス: 302。
- ○ `Location`: `/ytsched/`。
- ○ POST 後の `trash.jsonl`: 0 bytes（空）。

## 4. Playwright による確認ダイアログ

`/usr/bin/chromium` と Playwright を使い、同じ一時 datadir のアプリを操作した。

- ○ ヘッダーの「空にする」を押して dialog を dismiss: URL は
  `/ytsched/trash` のまま、`trash.jsonl` は 2 件のまま。
- ○ 同じボタンで dialog を accept: URL は `/ytsched/` へ遷移し、
  週間表示の `#main` が visible、`trash.jsonl` は空。

## 後始末

- ○ サーバは Ctrl-C で停止を確認した。
- ○ `mise run upgradeproject` は実行していない。
- ○ ソース、テスト、TODO.md は変更していない。
