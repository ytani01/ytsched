# TODO-041 verifier 報告

## 1. lint とテスト

```sh
mise run lint
mise run test
```

- `ruff format` : 23 files left unchanged
- `ruff check` : All checks passed!
- `basedpyright` : 0 errors, 0 warnings, 0 notes
- `mypy` : Success: no issues found in 20 source files
- `pytest` : **418 passed** in 3.04s

○ 問題なし。

## 2. 追加読み込みの直後に、狙った位置へ一度で移るか

一時 datadir（`/tmp/.../todo041/data`、データ無し）で
`uv run ytsched webapp --datadir <一時dir> --port 10098` を起動し、
Playwright（`uv run --no-project --with playwright python <script>`、
Chromium 実行ファイル指定、viewport 412x915）で依頼書どおりの手順を実行。

```js
window.scrollTo({top: document.body.scrollHeight, behavior:'instant'})
scrollHdr('manual')
```

結果:

| | 値 |
|---|---|
| 追加読み込み直後の `scrollY` | **2611** |
| `sde_align` | `bottom` |
| `scrollToId` が狙った位置 | **2611** |

`scrollY` と狙った位置が一致し、修正前の `0`（動かない）から改善している。
コンソールログにも `scrollToDate:date=2026-10-07, sde_align=bottom` →
`scrollToId:sde_align=bottom` → `scrollHdr:d_top=2611, d_bottom=3270` と
一致する流れが出ている。

○ 直っている。

## 3. ボタン操作の smooth が残っているか

`<`（`#back_button`）／`>`（`#forward_button`）／ホームボタン
（`#home_button`）をこの順で headless クリックし、`date` input の値と
コンソールログを確認。

| 操作 | date の変化 |
|---|---|
| 初期 | 2026-08-24 |
| `#back_button` クリック後 | 2026-08-17（`moveToMonday:days=-7` → `date-2026-08-17` へ scroll） |
| `#forward_button` クリック後 | 2026-08-24（`moveToMonday:days=7` → `date-2026-08-24` へ scroll） |
| `#home_button` クリック後 | 2026-08-24（`scrollToDate:date=2026-08-24` へ scroll） |

`page.on("pageerror")` によるエラーはゼロ。`moveToMonday` /
`scrollToDate` / `scrollToId` の呼び出しがログどおりに流れており、
遷移すべきタイミングで遷移している。headless では smooth アニメーションが
走らないため `scrollY` 自体は動かない想定どおりで、依頼書の判定基準
（エラーが出ないか・遷移するはずのときに遷移するか）を満たす。

○ 問題なし。

## 補足

- サーバのログ（`server.log`）に例外・トレースバックは出ていない
  （`start server: run forever ..` の INFO のみ）。
- 使用した Playwright スクリプトは
  `/tmp/claude-649/-home-ytani-work-ytsched/930db278-6388-46ee-baa2-58208dfcf8cc/scratchpad/todo041/check.py`
  と `check2.py`（スクラッチパッド、リポジトリ外）。
- 確認後、`uv run ytsched webapp` のプロセスは kill 済み。実データ
  （`~/ytsched/data`）は使っていない。

## 判断が要る点

なし。3 項目すべて問題なし。
