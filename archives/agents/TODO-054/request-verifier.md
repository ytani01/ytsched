# TODO-054 verifier への依頼

左右のスワイプで週を送る機能を入れた（TODO-054）。**実際に動くか**を
確かめてほしい。

## 変更したもの

- `src/ytsched/webroot/static/js/my.js` — 末尾にスワイプの処理を追加
  （`touchStartHdr` / `touchMoveHdr` / `touchEndHdr` / `touchCancelHdr`）
- `src/ytsched/webroot/templates/main.html` — 上の 4 つを `window` に登録

`git diff` で見られる。

## やってほしいこと

### 1. 決まった手順

```
mise run fmt
mise run typecheck
mise run lint
mise run test
```

出力をそのまま報告に貼る。**`mise run upgradeproject` は走らせない。**

### 2. 実際に動かす

**`--datadir` には必ず一時ディレクトリを指定する**（`~/ytsched/data` の
実データを汚さない）。ポートは 10085 以外を使う（10085 は main が
使っている）。

```
uv run ytsched webapp --port 18054 --datadir <一時ディレクトリ>
```

データが空だと週が出ないので、`{datadir}/2026/08/*.jsonl` などに
何件か置くこと（形式は `docs/data-format.md`）。今日は 2026-08-26。

playwright でタッチのスワイプを送る。`page.touchscreen` には `tap` しか
無いので、CDP の `Input.dispatchTouchEvent` を使う。文脈は
`browser.new_context(viewport=..., has_touch=True, is_mobile=True)`。
ブラウザはシステムの `/usr/bin/chromium`、`env -u DISPLAY` を付ける。

確かめること（`#cur_day` の値で判断できる）:

- **左へ払うと次の週へ、右へ払うと前の週へ動く**
- **縦の動きが優勢なスワイプでは週が変わらない**（例: dx=90, dy=400）
- **横に 60px 未満しか動かないと週が変わらない**
- **画面の左端・右端から始めたスワイプでは週が変わらない**
  （iOS Safari の画面端スワイプと競合させないため）
- **800ms より長く触れていたら週が変わらない**
- **ピンチ（2 本指）では週が変わらない**
- **検索欄の上で始めたスワイプでは週が変わらない**
- **ゲージの針が動いて見える**（週が変わった直後に `#gage_r` の
  `bottom` を短い間隔で読むと、前の週の位置から今の週の位置へ
  0.3 秒かけて動く）
- **縦スクロールが今までどおりできる**（`passive` で登録しているので
  スワイプの判定がスクロールを止めないこと）
- 上の一連の操作で、JavaScript のコンソールに error / warning が
  出ないこと、サーバのログに例外が出ないこと

### 3. 編集画面ではスワイプが効かないこと

登録しているのは `main.html` だけ。`/ytsched/edit/` でスワイプしても
何も起きないことを確かめる。

## 報告

`archives/agents/TODO-054/verifier-report.md` に書く。返事は 5 行以内で
「終わったか・報告ファイルのパス・判断が要る点」だけ。

**コードは直さない。** 見つけたことは報告するだけにする。
