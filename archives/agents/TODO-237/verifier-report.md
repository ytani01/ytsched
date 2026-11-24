# verifier 報告 TODO-237

## 1. 静的確認・テスト
- ○ `mise run fmt`: 45 files left unchanged、`git diff --stat` は前後で同じ
- ○ `mise run lint`: All checks passed!（eslint も通過）
- ○ `mise run typecheck`: basedpyright 0 errors / mypy Success: no issues found in 42 source files
- ○ `uv run pytest -q tests/test_attach.py`: 16 passed

## 2. 壊して落ちるか（attach.py / trash_handler.py。複製から書き戻し済み。最後の `git diff --stat` は開始時と同じ）
- ○ A `is_valid_name` を `return True` → `test_handler_rejects_path_traversal` が失敗
- ○ B `safe_name` の `rsplit("/")` を外す → `test_safe_name` が失敗
- ○ C ゴミ箱の「他の版が残る」判定を無効化 → `test_delete_from_trash_keeps_dir_if_live_version_exists`、`..._if_version_left_in_trash` が失敗
- ○ D 「フォルダがあるか」の条件を常に continue → `test_delete_from_trash_removes_orphan_dir` が失敗

## 3. 画面（--datadir は一時ディレクトリ、port 10187、1280x800）
- ○ PNG(20x20)+PDF を添付して保存 → `attachments/{UUID}/` に pic.png / doc.pdf
- ○ 詳細を開く: img の naturalWidth = 20。PDF は `doc.pdf` のリンク（href は `/ytsched/attach/{UUID}/doc.pdf`）
- ○ 編集で doc.pdf だけ外して保存 → ディスク上は pic.png のみ
- ○ 予定を削除（添付は残る）→ ゴミ箱から削除 → `attachments/` 配下が空（フォルダごと消えた）
- 補足: ゴミ箱に 3 件並んでいた（同じ UUID の複数の版と見られるが未確認）。1 件にチェックして削除したところ、ゴミ箱の全件が消えフォルダも消えた。チェックが 1 件分で済んだのか全件に及んだのかは確かめていない
- スクリーンショット: archives/agents/TODO-237/verifier-detail.png（詳細を開いた画面）。目で見て、添付 2 件のうち PDF リンクと画像（赤い四角）が出ている
- サーバのログに Traceback / Error は無し

## 4. 添付 URL のパス（curl --max-time 5 --path-as-is）
- 正常 `attach/{UUID}/a.txt` → 200（ダウンロード扱いで 3 バイト）
- `{UUID}/..%2F..%2Fconf.json`、`{UUID}/../../conf.json`、`..%2Fconf.json`、`../conf.json`、`%2e%2e/conf.json`、`{UUID}/%2e%2e%2f%2e%2e%2fconf.json`、`{UUID}/..%5Cconf.json` → すべて 404
- 外のファイル（conf.json）の中身は返らなかった

## 5. mermaid
- ○ `src/README.md` 133〜214 行のクラス図を d1.md に分けて描画、PNG を開いて確認（archives/agents/TODO-237/verifier-classdiagram.png）。AttachHandler（StaticFileHandler を継承）、AttachStore、HandlerBase の `get_template_namespace()` が描かれ、欠けは無い。矢印のラベル同士が近い箇所があるが、重なりで読めなくなってはいない（境界線上。判断は main）。
- 描画には chromium の `--no-sandbox`（puppeteer 設定ファイル）を付けた

## 後始末
- webapp のプロセスは kill 済み（pgrep で残りなし）。実データには触れていない

## ゴミ箱の確かめ直し
前回は「すべて選択」を押した可能性がある。今回は `input.my-trash-select[data-sde-id]` の 1 つだけをチェックした。
同じ UUID の版が 2 件ゴミ箱に入る状態（作成 → 編集で版 2 → 削除）で実施。
- 削除前: ゴミ箱 2 件（`{UUID}-1`、`{UUID}-2`）、`attachments/{UUID}/` あり
- (a)(b) ○ 1 件だけ削除 → ゴミ箱 1 件（`-1`）が残り、`attachments/{UUID}/` も残った
- (c) ○ 残り 1 件を削除 → ゴミ箱 0 件、`attachments/` 配下は空（フォルダが消えた）
- 前回の「全件が消えた」は、`.first` が「すべて選択」だったためと見られる（今回の結果と矛盾しない。確かめてはいない）
