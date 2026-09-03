# TODO-177 検証報告

## 確認した項目

1. `uv run pytest -q` — 665 件通過（実装者が触った 2 件含む）。○
   ```
   cd ~/work/ytsched && uv run pytest -q
   ```
2. `uv run ruff check` / `ruff format --check` — 問題なし。○
3. アプリ起動 — 一時データディレクトリで `uv run ytsched webapp --datadir <tmp> --port 19990` を
   起動、`curl` で `/ytsched/edit/?date=2026-09-04` に 200。ログに例外・トレースバックなし。○
4. HTML の展開確認 — 取得した HTML に `{{ ` `{%` の生残りなし。○
5. `id` の重複 — `grep -o 'id="..."' | sort | uniq -d` で重複ゼロ。
   ボタン帯・メニューは `class` のみで `id` を持たないため衝突しない。○
6. 新規作成時（`sde_id` 省略の URL）— 上下とも複製ボタン
   （`data-cmd="add"`）が 0 件で出ない。○
   既存の予定（`sde_id=7f3c1a9e-2b64-4d18-9a5e-0c8b3d6f1e27-3` を指定）
   — 上下とも複製ボタンが 1 件ずつ、計 2 件出る。○
7. `sde_id` 欄の全桁表示 — playwright で
   `scrollWidth === clientWidth`（286 === 286、`value` は 38 文字）を確認。
   はみ出しなし。○
8. 上部の帯でフォーム先頭が隠れないか — playwright の bounding box で
   上部帯の高さ 45px、`#title` の `y` 座標 168px。隠れていない。○
9. `edit-page.js` が両方の帯を拾うか — playwright で `.my-edit-bar-top`
   内の `[data-action="back"]` を実際にクリックし、
   `http://.../ytsched/?date=2026-09-04` へ遷移することを確認。○
10. キーボード追従 — `keyboard.js` は
    `getElementsByClassName("my-follow-keyboard")` を使っており、
    このクラスは実装上フッター（`my-edit-bar-bottom`）にしか付いていない
    （grep で確認）。上部の帯を持ち上げる経路は無い。○

## 見つかった問題

なし。要件 1〜7 とも実装者の報告どおり動作している。

## 残る懸念（判断は main へ）

- 上部ボタンの押下テスト（`back`）は playwright で確認したが、
  `update` / `fix` / `add`（複製）/ `del`（削除）を**上部ボタンから**
  実際に押す自動テストは無い（`tests/test_browser.py` は `.first` で
  下部を含む先頭要素を触っているだけで、上部専用のケースは無い）。
  下部と同じリスナー登録経路（`querySelectorAll(".my-edit-bar")` で
  同一関数を両方に付与）なので実質的なリスクは低いとみるが、
  自動テストとして残すかどうかは main の判断。
