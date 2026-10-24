# TODO-226 verifier 報告

対象: `src/ytsched/webroot/static/js/edit-page.js` の `keyDownHdr`（未コミット）。
結果: 4 手順すべて ○。食い違い無し。

## 条件
- サーバー: `uv run ytsched webapp --port 10111 --datadir <一時ディレクトリ>`（port 10099 は触っていない）
- ブラウザ: Playwright（Python）+ `/usr/bin/chromium`、画面 1280x800
- 操作スクリプト: `/tmp/claude-649/-home-ytani-work-ytsched/def1b2f2-90b6-40c6-99c1-ec9231d3d0c7/scratchpad/check.py`
- URL: `http://localhost:10111/ytsched/edit/`（新規の編集画面）

## 結果
1. ○ 件名に `TODO226-t1` → Ctrl+Enter: `POST http://localhost:10111/ytsched/`（本文に `cmd=fix`）→ `/ytsched/?date=2026-10-24&sde_align=top` へ移動。週の表示に `TODO226-t1` あり。保存先 `2026/10/24.jsonl` に `"title": "TODO226-t1"`
2. ○ 詳細で `a` → Enter → `b`: URL は `/ytsched/edit/` のまま、POST 0 件、`detail` の値は `'a\nb'`
3. ○ 続けて Ctrl+Enter: `POST /ytsched/`（`cmd=fix`）→ `/ytsched/?date=2026-10-24&sde_align=top` へ移動。保存先に `"title": "TODO226-t2"`、`"detail": "a\r\nb"`
4. ○ 件名で Enter 単独: URL は `/ytsched/edit/` のまま、POST 0 件、件名の値は `TODO226-t4` のまま

## その他
- サーバーのログに `Traceback` / `ERROR` なし
- IME 変換中（`isComposing`）は依頼どおり確かめていない
- 起動した uv と ytsched の 2 プロセス（PID 88573・88580）を kill 済み。port 10111 は閉じた
- `git diff --stat` は始める前と同じ（`docs/UsersGuide.md` +2、`edit-page.js` +16）。依頼に無い変更なし
