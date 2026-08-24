# TODO-039 verifier への依頼

スマホ用の設定（アイコン一式・`manifest.json`・ソフトキーボード対策）を
足した。**実際に動くか**を確かめてほしい。

実装の中身は
[implementer-report.md](implementer-report.md) と
[implementer-request.md](implementer-request.md) にある。

## 確かめてほしいこと

### 1. いつもの一式

- `mise run test`（`fmt` → `typecheck` → `test` の順に走る）。
  **件数を報告に書く**（直前は 412 件 pass）
- `uv run ruff format --check` 相当のことは `mise run fmt` に含まれる

### 2. `uv build` した wheel の中身

`mise run build` で作った wheel に、次が入っていること。

```
ytsched/webroot/static/manifest.json
ytsched/webroot/static/favicon.ico
ytsched/webroot/static/icons/icon.svg
ytsched/webroot/static/icons/icon-192.png
ytsched/webroot/static/icons/icon-512.png
ytsched/webroot/static/icons/icon-maskable-512.png
ytsched/webroot/static/icons/apple-touch-icon.png
```

`unzip -l dist/*.whl` で見られる。

### 3. 起動して、実際に引く

`uv run ytsched webapp --datadir <一時ディレクトリ> --port <空きポート>` を
`run_in_background` で起動して、curl で確かめる。
**`~/ytsched/data` は使わないこと。**

- `/ytsched/`・`/ytsched/edit` が 200
- `/ytsched/static/manifest.json` が 200 で、`python3 -m json.tool` に
  通る（JSON として読める）
- 上の 7 ファイルが全部 200 で返る
- **`favicon.ico` が本物の ICO であること。** 先頭 4 バイトが
  `00 00 01 00`（`xxd` で見る）。`file` コマンドが
  `MS Windows icon resource` と言うこと。**直前まで、中身が PNG なのに
  `.ico` という名前が付いていた**ので、ここは必ず見てほしい
- PNG 4 つの先頭が `\x89PNG`、`icon.svg` の中身が `<svg` で始まること
- 一覧の HTML に `rel="manifest"`・`rel="apple-touch-icon"`・
  `rel="icon"`・`name="theme-color"` の行が出ていること
- HTML に `{{` や `{%` が生で残っていないこと

### 4. `--urlprefix` を変えても付いてくるか（**ここが要点**）

`manifest.json` の `start_url` と `scope` を `../` にしてあるのは、
**URL prefix を変えても付いてくるようにするため**。効いているかを見たい。

`--urlprefix /sched` を付けて起動し直して、

- `/sched/static/manifest.json` が 200
- `/sched/` が 200
- 一覧の HTML の `<link rel="manifest" href="…">` が
  `/sched/static/manifest.json?v=…` になっている
  （`/ytsched/…` が残っていない）
- manifest の `start_url` が `../` のままであること（中身は変わらない。
  変わるのは manifest 自身の URL で、そこから相対で解決される）

**`../` が本当に `/sched/` に解決されるかは、ブラウザの仕事なので
curl では見えない。** そこまでは求めない。上の 4 つで十分。

### 5. ブラウザで見る（chromium があれば）

- 一覧・編集の 2 画面 × 幅 412 / 740 で、JavaScript の例外
  （`Uncaught` / `TypeError` / `ReferenceError`）が 0 件
- `HEAD`（`e146a11`）と画素単位で比べて、**下部バーの位置と見た目が
  変わっていないこと**。キーボードが無い状態では `followKeyboard()` の
  ずれは 0 になるはずなので、差はほぼ出ないのが期待
- `window.visualViewport` が無い環境でも例外にならないこと
  （`--headless` で `visualViewport` を `undefined` にして評価する、
  などの方法があれば）

**申し送り（TODO-040 で verifier がつまずいた点）。**
chromium を続けて起動するときは、呼び出しごとに `--user-data-dir` に
別のディレクトリを渡すこと。指定しないと既定のプロファイルのロック待ちで
**無期限に止まる**（`timeout` を超えても終わらない）。

## 既知で、報告しなくてよいこと

- **アイコンの見た目**は main が確認済み（32px まで縮めて形が残ることも
  見た）。良し悪しは見なくてよい
- **実機のスマホでの確認はできない。** ソフトキーボードが実際に出る環境が
  無いので、キーボードの上にボタンが出るかどうかは利用者が確かめる。
  ここで見てほしいのは「キーボードが無い状態で今までどおりか」と
  「例外が出ないか」
- `changeDetailHeight()`（編集画面の textarea の高さ）は読み込み時に
  1 回しか計算しない。キーボードが出ても高さは変わらない。これは
  今回の範囲外

## 決まりごと

- **コードを直さない。** 見つけたことは報告に書く
- `mise run upgradeproject` は走らせない
- 報告は `archives/agents/TODO-039/verifier-report.md`
