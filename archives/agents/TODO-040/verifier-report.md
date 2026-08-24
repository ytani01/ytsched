# TODO-040 verifier 報告

比較対象: コミット `1a6a4fd`（`git archive 1a6a4fd src/ytsched/webroot`
で取り出した旧版）と、現在の作業ツリー（新版）。

作業場所（すべて一時ディレクトリ、`~/ytsched/data` は未使用）:
`/tmp/claude-649/-home-ytani-work-ytsched/.../scratchpad/verify040/`

## 1. 画素単位の比較（結論: ○、想定内の差のみ）

### 手順

1. 旧版・新版それぞれを `--datadir` に一時ディレクトリを指定して別ポートで
   起動（旧: `-p 18001 -r <旧webroot> -w old_datadir`、新: `-p 18002
   -w new_datadir`）
2. 両方の datadir に同じ内容のテストデータを投入（下記「テストデータ」）
3. `curl` で一覧 (`/ytsched/`)・編集 (`/ytsched/edit?...`)・検索
   (`/ytsched/?search=会議`) の HTML を取得し、Python スクリプトで
   依頼書どおり 4 か所を置換
   - `window.addEventListener('load', onloadHdr);` → 空文字
   - `visibility: hidden;` → `visibility: visible;`
   - `class="longtext-sw d-none">` → `class="longtext-sw d-none" checked>`
     （**依頼書の `class="longtext-sw"` という完全一致パターンでは
     マッチしなかった。実際は `class="longtext-sw d-none">` という形。**
     パターンを合わせて修正して撮った）
   - `id="menu-sw"` の `<input>` に ` checked` を追加
4. `python3 -m http.server` で配信（`ytsched/static` へのシンボリック
   リンクを配信ルート下に作成）
5. `chromium --headless --disable-gpu --hide-scrollbars --no-sandbox
   --virtual-time-budget=5000 --window-size=<幅>,4000 --screenshot=…`
   で撮影
6. `compare -metric AE 旧.png 新.png null:` で比較

**つまずいた点（main への申し送り）:** 複数の chromium
プロセスを `--user-data-dir` を指定せずに続けて起動すると、既定の
プロファイルディレクトリのロック待ちで**無期限にハングする**
（`timeout 120` を超えても終わらない）。呼び出しごとに
`--user-data-dir=<固有のディレクトリ>` を指定したら再現しなくなった。
依頼書の手順にはこの注意が無かったので、次に同種の作業をするときのために
書いておく。

### テストデータ

依頼書の指定どおり、旧版・新版の datadir に同じ内容を投入（`sde_id` は
乱数なので旧新で異なるが、それ以外は同じ）。

- 通常の予定（2026-08-20、詳細に改行あり）
- ★重要・(重要) の予定（2026-08-21 × 2 件）
- 取り消し（`x …`、`(欠)…`、2026-08-22 × 2 件）
- 祝日（`type: "祝日"`、2026-08-23）
- 場所あり・複数行の詳細（懇親会、2026-08-24）
- ToDo: 期限切れ（2026-08-10）、1 週間以内（2026-08-27）、先
  （2026-09-15）

### 撮った画面と AE（旧×新）

同じ幅・全体高さ 4000px で撮影。総画素数は 412 幅で 1,648,000、
740 幅で 2,960,000。

| 画面 | 幅 | 総画素数に対する違う画素（AE） |
|---|---|---|
| 一覧 | 412 | 22,534 |
| 一覧 | 740 | 22,656 |
| 編集 | 412 | 17,291 |
| 編集 | 740 | 22,474 |
| 検索 | 412 | 22,530 |
| 検索 | 740 | 18,406 |

### chromium 自身の揺らぎ（同じ版で 2 回撮って比較）

新版の一覧 412 幅を 2 回撮って比較: AE = 4,590（1,648,000 画素中、
0.28%）。上表の AE（1.0〜1.4%）は揺らぎの数倍あり、実装差が乗っている
ことが分かる。

### 内訳（diff 画像を目視確認）

`compare 旧.png 新.png diff.png` で作った差分画像を目視した
（`~/tmp/playwright-mcp/todo040_*.png` に保存済み。チャットにも添付）。

- **Font Awesome の絵柄の差** — 一覧・編集・検索のどの画面でも、
  日付ブロックごとに小さな「＋」アイコン（新規追加ボタン）が変わっている。
  旧版は太く丸みのある形、新版は細く小さい形。編集画面では上部の
  複製・削除ボタンや、フッターのアイコン群にも同様の変化がある。
  依頼書に書かれた「絵柄が変わるのは了承済み」の範囲内で、位置や大きさの
  ずれは無い
- **読み込み中のしるしの回転位置** — 一覧・検索の 8/2〜8/3 付近と、
  編集画面の中央付近に、`fa-spin` の円環アイコンが写っている。旧新で
  回転角度が違うだけで、実装の差ではない
- **上記 2 つで説明の付かない差は見つからなかった。** 行の位置・幅・
  色のずれは見当たらない

### ページ全体の高さ・日付ブロックの高さ

`getBoundingClientRect()` を仕込んだ HTML を `chromium --dump-dom` で
読んだ。

| | 旧版 | 新版 |
|---|---|---|
| `document.body.scrollHeight` | 6980px | 6980px |
| `.my-date-block` の高さ | 75px | 75px |

**完全一致。** `my.css` の `--bs-body-font-family` 固定が効いている。

## 2. そのほか（結論: 全て ○）

- `mise run test`: **412 件 pass**（fmt / typecheck / lint も通過。
  `ruff check` 全チェック通過、`basedpyright` 0 errors、`mypy` no
  issues）
- 一時 datadir でアプリを起動し、一覧・編集・検索が 200 で返る
  （`curl -s -o /dev/null -w "%{http_code}"`）。サーバのログ
  （old/new とも）に `Traceback` / `error` は 0 件（`grep -i -c`）
- 同梱した 5 ファイルが全て 200 で配信される
  （`bootstrap.min.css` / `fontawesome/css/all.css` /
  `fa-solid-900.woff2` / `fa-regular-400.woff2` /
  `fontawesome/LICENSE.txt` / `bootstrap/LICENSE`）
- `.woff2` の先頭 4 バイトは 2 ファイルとも `b'wOF2'`
- 消したはずの `.woff` 2 つは **404**。`all.css` にも `.woff`（`.woff2`
  以外）への `url(...)` 参照は 0 件、テンプレートにも `.woff` への参照
  無し
- `uv build` した wheel（`ytsched-0.3.2.dev3+gb9579b57c.d20260824-py3-none-any.whl`）に
  `bootstrap.min.css` / `LICENSE` / `all.css` / 各 `LICENSE.txt` /
  `.woff2` 2 つが入っている。`.woff` は入っていない
- ブラウザの JavaScript 例外は 0 件（一覧・編集 × 412 / 740 の
  4 通り、`--enable-logging=stderr` で `Uncaught` / `TypeError` /
  `ReferenceError` を grep）
- `grep -rn 'text-left\|text-right\|font-weight-bold' src/` → 0 件
- `git diff 1a6a4fd -- src/ytsched/*.py src/ytsched/webroot/static/js/`
  → 0 行（Python と `my.js` は変わっていない）
- `README.md` の該当箇所を確認。Bootstrap 5.3.8、Font Awesome 7.3.1、
  「`woff2` のみ同梱・`solid`/`regular` のみ」の記述に書き直されている

## プロセスの後始末

自分で立てたプロセス（`ytsched webapp -p 18001/18002`、
`python3 -m http.server 18011/18012`）は `pgrep -af` で PID を確認して
から `kill` し、全て終了を確認した。利用者のサーバ（`-p 12345`、
PID 5182）は触っていない。

**気づいたが自分が始めたものではないもの:** `python3 -m http.server
10190/10191/10194` が確認開始時点で既に動いていた（自分が起動したもの
ではないので停止していない）。他の作業の残骸の可能性がある旨だけ報告する。

## 見つかった不具合・気になった点

- 実装・テストとも問題は見つからなかった
- 依頼書の画素比較手順（`class="longtext-sw"` への置換）と実際の HTML
  （`class="longtext-sw d-none">`）が食い違っていた（上記「1. 画素単位の
  比較」参照）。コードの不具合ではなく、依頼書側の記述の話
