# TODO-069 verifier 報告

対象は `git diff`（未コミット）。

## lint / test

- `mise run lint` ○（ruff format / ruff check / basedpyright / mypy すべて通過）
- `mise run test` ○ 453 件通過（`uv run pytest tests`）

## ブラウザでの実機確認（`--datadir /tmp/todo069-verify`、playwright + chromium）

以下すべて○（`window` に置いた目印が残っているかで「読み直していないこと」を確認）。

- 既定（`LoadMonths` 未設定）で `.my-week-panel` が 9 枚（前後 4 週 + 今週）
- ◀▶ で週を送れる。**4 回までは目印が残り、読み直しが起きない**
- **5 回目で範囲の外に出て、そこで初めて読み直す**（目印が消え、`load` イベントが発生。ラベルは `+5w` のまま正しい）
- 読み直し後、`.my-week-panel` はまた 9 枚に戻る
- ヘッダのゲージのラベル（`±0`→`+4w`→`-4w` など）が移った先の週に合う
- `history.back()` / `go_forward()` で週が戻る・進む
- ホームボタン: 範囲内なら 1 回タップで読み直さず今日の週へ、ダブルタップで読み直す
- 検索モード（`?search_str=...`）は `.my-week-panel` が 1 枚のまま、壊れていない
- スワイプ（headless では mouse のドラッグで代用）でも週が送れる
- `page.on("pageerror")` / console error とも 0 件

body の高さについては、初期表示 616px → 4 回送った後 612px と、送った週の内容量に応じて変わることを確認（`my-week-cur` の付け替えは効いている）。

## `conf.json` の `LoadMonths`

`/tmp/todo069-verify` で `conf.json` を書き換えて確認（`.my-week-panel` の数）。

| `LoadMonths` | panel 数 | 期待 |
|---|---|---|
| `"0"` | 1 | ○ |
| `"3"` | 27 | ○（4×3×2+3） |
| `"abc"` | 9 | ○ 既定 1 ヶ月へフォールバック |
| `"99"` | 9 | ○ 既定へフォールバック |

サーバログに `LoadMonths='abc': invalid literal for int() ... ignored` / `LoadMonths='99': LoadMonths must be in 0..6, not 99 .. ignored` の WARNING のみで、例外・トレースバックは出ていない。

**注意**: 最初の 1 回目、`conf.json` に前のテストで書いた `SearchStr: "test"` が残っていて全部 1 枚になった。`SearchStr` を消すと期待どおりに直った。実装の不具合ではなく、こちらの確認手順の問題。

## 速さの比較（実データ、`/home/ytani/.claude/jobs/b5621731/tmp/realdata`）

`git stash` で変更前へ戻し、同じデータで別ポートに起動して比較（**必ず `git stash pop` で戻した。作業後の `git diff --stat` は元どおり**）。

- **HTTP リクエストが飛ぶかどうか**という点では、狙いどおりの差が出ている。
  - 変更前: forward クリック後 109ms で `GET /ytsched/?date=...` が飛ぶ（ページ全体を読み直す）
  - 変更後: forward クリックしても本体の GET は飛ばない（favicon 相当の `icon.svg` だけ）。5 回目で範囲外に出たときだけ本体の GET が飛ぶ
- 一方、**クリックしてから次の操作ができるまでの体感時間**を計測すると、変更前が 95〜120ms、変更後が 273〜302ms で、**変更後のほうが遅く見えた**。ただし変更後の値は `moveToMonday()` 内の `slideWeekWrap()` のスライドアニメーション（`SWIPE_SLIDE_MSEC=200ms`、変更前後で同じ値）の待ち時間をほぼそのまま含んでいるのに対し、変更前の 95〜120ms は同じアニメーションを経ているはずなのに 200ms 未満だった。**headless chromium でこの CSS transition が実時間どおり進んでいない可能性があり、この数値だけで優劣を断定できるか自信が無い**。この点は判断が要る（下記）。
- サーバ側の応答自体は速い（実データでも forward 後の GET は 100ms 前後）。TODO の文書にある「重いのは HTML の描き直し」という前提の検証は、この計測方法では不十分だった。

## 判断が要る点

- **速さの実測が、狙いどおりの結果になっていない。** HTTP リクエストが飛ばなくなったことは確認できたが、体感時間の単純比較では変更後のほうが遅く見えた（変更前 95〜120ms、変更後 273〜302ms）。原因は `slideWeekWrap()` の 200ms のスライドアニメーション（前後で変更なし）が影響している可能性が高く、headless 環境での計測の信頼性そのものに疑問がある。**この数値をどう扱うか（実機の手元で体感を確認する／計測方法を変える／気にしない）は main の判断が要る。**
