# TODO-051. `DISPLAY` があると画面のキャプチャが撮れないのを直す（保留）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier |

- [ ] `tools/screenshot.py` が `DISPLAY` を外して chromium を起動するようにする
- [ ] `DISPLAY` がある状態と無い状態の両方で撮れることを確かめる
- [ ] `docs/Developer.md` の「画面を撮る」に、この事情を書き足す

**2026-08-25 に着手したが、症状が再現しなかったので保留にした。**

### 症状

TODO-047 で分かった。`DISPLAY=localhost:11.0`（ssh の X11 転送）が設定されて
いると、`Page.screenshot()` が「fonts loaded」の直後で 30 秒待ってタイムアウト
する。`env -u DISPLAY` を付けると通る。playwright 1.55.0・1.58.0・1.61.0・
1.62.0 の 4 つ、chromium の起動オプション 4 通り（`--disable-gpu` ほか）、
`<h1>hello</h1>` だけのページでも同じで、ページの高さも関係なかった。

### 保留にした理由

**2026-08-25 に、同じ条件（`DISPLAY=localhost:11.0`、playwright 1.62.0、
chromium 151.0.7922.137）のはずが、どの撮り方でもそのまま撮れた。** 環境に
よって出たり出なかったりすることになり、直したかどうかを確かめられない。
当時の X サーバーは、もう同じものを用意できない。

また撮れなくなったら、**そのときの `DISPLAY` と X サーバーの様子を控えてから**
着手する。headless で動かす以上 `DISPLAY` は要らないので、直し方は「常に外す」
でよさそうだという見立ては変わっていない。

### ついでに決めたこと

`DEF_URL` に `--urlprefix` の既定（`/ytsched`）が入っていなかった件は、
`http://localhost:10085/ytsched/` にすると決めて直した（2026-08-25）。編集画面は
前置きが無いと 404 になるため。`docs/Developer.md` の「画面を撮る」にも書いた。

### 確かめ方

- `DISPLAY` を設定した状態で `mise run shot` が通ること。
  **これが今できないことなので、いちばん大事**
- `env -u DISPLAY` を付けた状態でも今までどおり通ること
- 保存された PNG が壊れていないこと（`file` で見る）
