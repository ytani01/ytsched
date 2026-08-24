# TODO-040 verifier への依頼

Bootstrap を 4.5.0 → 5.3.8、Font Awesome Free を 5.6.1 → 7.3.1 に上げた。
**`TODO.md` の TODO-040 と
`archives/agents/TODO-040/implementer-report.md` を先に読むこと。**

この項目の眼目は「**上げても表示が変わらない**」こと。テストは通るが
崩れは捕まえない（TODO-037・038 と同じ）。**確認の中心は画素単位の比較。**

## 比べる相手

**コミット `1a6a4fd`**（TODO-038 が済んだ状態＝上げる前の最後の版）。

```bash
git archive 1a6a4fd src/ytsched/webroot | tar x -C <一時ディレクトリ>
```

`b9579b5` は `TODO.md` しか変えていないので、`webroot` の中身は同じ。

## 絶対に守ること

- **`~/ytsched/data` を触らない。** 起動するときは `--datadir` に必ず
  一時ディレクトリを指定する
- **ポート 12345 で動いている利用者のサーバを止めない。** 作業で立てた
  プロセスだけを、`pgrep` で PID を確かめてから kill する
  （`pkill` はパターンで自分のシェルを巻き込む）
- コードを直さない。見つけたことは報告するだけ

## 1. 画素単位の比較（いちばん大事）

### 一覧の画面はそのまま撮れない

`main.html` は `window.addEventListener('load', onloadHdr)` で今日の位置
まで JavaScript がスクロールする。`chromium --headless --screenshot` で
そのまま撮ると**スクロール後の位置が写り、真っ白になることがある**
（main が実測した）。TODO-038 の verifier と同じく、**静的な HTML を
作ってから撮る**こと。

やり方（main が実際に通した手順）。

1. 旧版・新版をそれぞれ別ポートで `ytsched webapp` として起動する
   （`-r` に `webroot`、`-w` に一時 datadir を渡す）
2. `curl` で一覧と編集の HTML を取り、次の 4 つを置換して保存する
   - `window.addEventListener('load', onloadHdr);` → 空文字（JS の
     スクロールを止める）
   - `visibility: hidden;` → `visibility: visible;`
   - `class="longtext-sw"` → `class="longtext-sw" checked`（詳細を開く）
   - `id="menu-sw"` の `<input>` に ` checked` を足す（メニューを開く）
3. `python3 -m http.server` で配信する。`static_url()` が
   `/ytsched/static/…` を出すので、配信ルートの下に `ytsched/`
   ディレクトリを作り、その中に `webroot/static` へのシンボリックリンクを
   置く
4. `chromium --headless --disable-gpu --hide-scrollbars --no-sandbox
   --virtual-time-budget=5000 --window-size=<幅>,4000 --screenshot=…`
5. `compare -metric AE 旧.png 新.png null:`

### 撮る画面

一覧・編集・検索を **412 幅と 740 幅**で。詳細を全部開いた状態と、
メニューを開いた状態を含めること。

### テストデータ

一覧に中身が無いと比較の意味が薄い。普通の予定・★重要・取り消し
（`x` と `(欠`、複数行の詳細付き）・祝日・場所あり・ToDo（期限が過去 /
1 週間以内 / 先）を入れること。**旧版と新版で同じ内容にする**
（`sde_id` が違うのは構わないが、編集画面を撮るときは `sde_id` が
画面に出るので注意）。

### 差が出たときの切り分け

**差が出ること自体は想定内。** 内訳を分けて報告してほしい。

- **Font Awesome の絵柄** — **了承済み**。5 → 6 でアイコンが描き直され、
  家（`fa-home`）が輪郭線から塗りつぶしになるのがいちばん目立つ。
  リスト（`fa-list-alt`）・虫眼鏡（`fa-search`）・`fa-backspace` の ×
  も変わる。**直す対象ではないが、どのアイコンがどう変わったかは
  報告してほしい**（利用者が見て決める）
- **読み込み中のしるしの回転位置** — `fa-spin` のアニメーションなので、
  撮るたびに角度が違う。実装の差ではない
- **chromium 自身の揺らぎ** — TODO-038 で確認済み。**同じ版で 2 回撮って
  比べ、揺らぎの大きさを測ってから**旧×新の数字を読むこと
- **上の 3 つで説明が付かない差** — これが本当に見るべきもの。
  位置がずれている、幅が違う、色が違う、といったものがあれば
  ファイルと箇所を特定して報告する

### main が実測した参考値

main は別のテストデータで先に測っている（412 幅・一覧・全 1,648,000 px）。

| | 違う画素 |
|---|---|
| Font Awesome だけ 7.3.1 | 110,296 |
| Bootstrap だけ 5.3.8（フォント固定なし） | 432,275 |
| Bootstrap だけ 5.3.8（**フォント固定あり**） | 17,033 |
| 両方（フォント固定あり） | 114,430 |

**データが違うので数字はそのまま比べられない**が、桁が大きく外れたら
何かおかしい。特に見てほしいのが次の点。

- **ページ全体の高さと、日付ブロック 1 個の高さが旧版と一致すること。**
  main の環境では `document.body.scrollHeight` が旧新とも 6,943px、
  `.my-date-block` の高さが旧新とも 75px で完全に一致した。ここが
  ずれていたら `my.css` の `--bs-body-font-family` が効いていない
  （測るには、HTML に `getBoundingClientRect()` を呼ぶ `<script>` を
  足して結果を `document.title` に入れ、`chromium --dump-dom` で読むと
  よい）

## 2. そのほか

- `mise run test` が通るか（前回は 412 件）。`mise run lint` も
  （`mise run upgradeproject` は**走らせない**）
- 一時 datadir でアプリを起動し、一覧・編集・検索が 200 で返る。
  サーバのログに `Traceback` が出ていない
- 同梱した 5 ファイル（`bootstrap.min.css` / `all.css` /
  `fa-solid-900.woff2` / `fa-regular-400.woff2` と各 LICENSE）が
  200 で配信される。**`.woff2` の先頭 4 バイトが `wOF2`** になっている
- **消したはずの `.woff` 2 つが 404 になる**こと。あわせて、出力された
  HTML と CSS のどこからも `.woff` を参照していないこと
  （`all.css` の `@font-face` を見る）
- `uv build` した wheel に vendor のファイルが入っている
- ブラウザの JavaScript の例外が 0 件（一覧・編集 × 412 / 740 の
  4 通りで `Uncaught` / `TypeError` / `ReferenceError` を見る）
- `grep -rn 'text-left\|text-right\|font-weight-bold' src/` が 0 件
- **`src/` の Python と `static/js/my.js` が変わっていない**こと
  （`git diff 1a6a4fd -- src/ytsched/*.py src/ytsched/webroot/static/js/`）

## 報告

`archives/agents/TODO-040/verifier-report.md` に書く。返事は 5 行以内。

確認した項目ごとに ○ / × と、**実際に得られた値**（AE の数字、HTTP
ステータス、テストの件数）。使ったコマンドも、main が再現できるように
書くこと。作業で立てたプロセスを全部止めたことも書く。
