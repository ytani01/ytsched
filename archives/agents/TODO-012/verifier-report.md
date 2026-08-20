# TODO-012 verifier の報告

不正な正規表現を入れられたときの扱い。実装（未コミット）を確認した。

## 1. lint / test

- `uv run pytest tests` → **174 passed**（実装報告と同数）
- `mise run lint` → `ruff check` で **84 件**のエラーで停止
  （TODO-015 の既存指摘。想定どおり）
- `main_handler.py` と `tests/test_web.py` に絞って
  `uv run ruff check --extend-select I` の件数を比較した。
  - 変更後: **23 件**
  - `git stash` で HEAD の状態に戻して同じコマンド: **25 件**
  - **増えていない（むしろ 2 件減っている）。** implementer の報告どおり
- `uv run ruff format --line-length 78 --check src tests` →
  14 files already formatted
- `uv run basedpyright src tests` → 0 errors, 0 warnings, 0 notes
- `uv run mypy src tests` → Success: no issues found in 14 source files

## 2. アプリの起動確認

`--datadir` は scratchpad 内の一時ディレクトリを使用。ポート 10099 で
起動し、curl で確認後、PID を確認して kill 済み。

- `filter_str=[`（不正）→ 予定 2 件とも表示されたまま、赤い知らせ
  「フィルタの正規表現が正しくないので、絞り込みを無視しています」が出て、
  入力欄に `value="["` が残る
- `search_str=(`（不正）→ 知らせ「検索の正規表現が正しくないので、
  検索していません」が出て、`目標件数`（検索モードのバー）は出ない。
  予定は消えない
- 両方不正（`filter_str=[&search_str=(`）→ 1 つの `alert` の中に
  「フィルタの正規表現が… / 検索の正規表現が…」と ` / ` 区切りで両方出る
- 正しい `filter_str=会議` → 該当 1 件だけに絞り込まれる（今までどおり）
- 正しい `search_str=歯医者` → `目標件数` バーが出て検索モードに入る
- `filter_str=!会議`（正しい否定）→ 会議が消え、歯医者だけ残る
- `filter_str=![`（`!` 付きだが中身が不正）→ 知らせが出て、絞り込みを
  無視して全件表示（否定の外し方が正しく判定されている）
- `search_n=3` を指定した検索 → 3 件目に達したところで打ち切られる
  （`検索対象15/20/25` の 3 件のみ表示。`search_count >= search_n` の
  打ち切りが機能している）
- ToDo（`買い物`）にも正しいフィルタ・不正なフィルタの両方が
  期待どおり効く（不正時は消えない、正しいときは絞り込まれる）
- サーバのログには `compile_re()` の `WARNING` 以外に例外・トレースバックは
  出ていない
- 取得した HTML に `{{ }}` や `{%` の生残りは無し

（テスト中、初回起動後にデータファイルを追加して確認しようとしたところ
一部の日付でスケジュールが表示されない現象に遭遇したが、これは
`SchedData` のキャッシュ（起動中に一度読み込んだ日付はファイルの
更新を拾わない）による、こちらの確認手順の問題。サーバを再起動して
データを揃えてから再確認し、正しく表示されることを確認した。
実装のバグではない）

## 3. 新しいテストの妥当性

implementer の報告どおり、`main_handler.py` と `main.html` だけ
`git stash` して `uv run pytest tests/test_web.py -k invalid` を
実行したところ、**4 failed, 1 passed** になることを確認した
（差分は無し）。`test_invalid_filter_str_is_saved` は保存の挙動を
変えていないので、変更前後どちらでも通るのは妥当。

## 結論

依頼の確認項目はすべて期待どおりの結果。不具合は見つからなかった。
