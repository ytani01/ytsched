# TODO-075 verifier 報告

対象: `git diff` に出た README.md / src/README.md / docs/Developer.md /
docs/data-format.md の 4 ファイル。コードは変更していない（`git status`
で確認済み）。

## 1〜8 の確認結果（すべて実物と一致）

1. ○ `icons.svg` の `<symbol` 数
   `grep -c '<symbol' src/ytsched/webroot/static/icons/icons.svg` → 22

2. ○ 無限スクロール記述の削除
   `src/ytsched/webroot/static/js/my.js` に `IntersectionObserver` や
   スクロールでの追加読み込みは無く、`SWIPE_*` 定数とハンドラで
   左右スワイプ処理があるのみ。「1 画面に 1 週間。左右のスワイプで
   週を送る」と矛盾しない。

3. ○ ゲージの位置とタップ挙動
   `main.html` の `#week_bar` は `class="my-gage-bar fixed-top ..."`
   （画面上部固定）。`onmousedown="gageBarClickHdr(event);"` があり、
   `my.js` にタップ位置から週を逆算する処理（TODO-074 のコメント、
   L71・L263 付近）がある。

4. ○ JSON Lines / `ytsched migrate`
   `docs/data-format.md` の記述、`src/ytsched/__main__.py` の
   `migrate` サブコマンド、`~/ytsched/data` の実データ（`.cgi` と
   `.jsonl` が両方ある）と一致。

5. ○ `LoadMonths` 既定 1・範囲 0〜24
   `src/ytsched/main_handler.py`:
   `DEF_LOAD_MONTHS = 1` / `LOAD_MONTHS_MIN = 0` / `LOAD_MONTHS_MAX = 24`

6. ○ `webroot/static/` の中身
   実際のファイル: `css/`, `js/`, `icons/`（svg・png 複数）,
   `manifest.json`, `favicon.ico`。「CSS・JS・アイコン・
   `manifest.json`・favicon」と一致。

7. ○ 個別コマンドの対象 `src tests tools`
   `mise.toml` の `[tasks.fmt]` `[tasks.typecheck]` も
   `src tests tools` で、`docs/Developer.md` と一致。

8. ○ `docs/data-format.md` の「実データは…リポジトリに入れられない」
   `~/ytsched/data` には実データ（`.cgi`／`.jsonl`）が存在し、
   「現在は空」という旧文言より新文言のほうが実態に合う。

## テスト

- `uv run pytest tests -q` → 457 passed（文書のみの変更なので想定どおり）

## 修正漏れのズレの探索

README.md / src/README.md / docs/Developer.md / docs/data-format.md /
tests/README.md / CLAUDE.md を対象に、旧い数値（23 個・0〜6 など）が
残っていないか grep したが、他に残存なし。`tests/README.md` に
コマンド対象への言及は無く、ズレの余地なし。CLAUDE.md にも該当の
数値記述なし。

## 判断が要る点

なし。8 件すべて実物と一致し、追加のズレも見つからなかった。
