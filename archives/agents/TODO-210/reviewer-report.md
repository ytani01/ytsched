# TODO-210 reviewer 報告

対象: `git diff -- src tests docs`（`save()`、`__make_backup()`、テスト 2 件、文書 2 か所）。
コードは直していない。実測は scratchpad のコピーと一時ディレクトリで行った（作業ツリーは変えていない）。

## 結論

確信度の高い不具合は無し。テストの弱い箇所が 1 つ、確信度の低い気づきが 3 つ。

## 一致したもの

- 通常の経路: 本体の inode は新しくなり、`.bak` は旧本体の inode だけを指す（実測: old_ino=408169 → `.bak`=408169、本体=408170）
- 差し替え（`tmp.replace(本体)`）で失敗したとき: 本体・`.bak` とも元の内容のまま残り、一時ファイルも一時リンクも残らない（テスト 1 と同じ条件）
- `os.link` 成功 → `replace(.bak)` が `OSError` のとき: 一時リンクを消してから `shutil.move` へ移る。ゴミは残らない（実測: `01.jsonl` と `01.jsonl.bak` だけが残る）
- `os.link` が `OSError` のとき: `shutil.move` へ移る。旧実装と同じ挙動
- 同じ inode の間に本体をその場で書き換える経路は無い。`pathname.open` の書き込みは `trash.py:91`（`trash.jsonl`、`SchedDataFile` ではない）と `conf.py:244`（設定ファイル）だけ。`fix_id.py:199-200` は一時ファイル経由の `replace()`。`migrate.py:325` は既存のファイルがあれば飛ばす
- 一時リンクの名前（`.01.jsonl.bak.<hex>`）は一時ファイル（`.01.jsonl.<hex>`）と衝突しない。`DAILY_GLOB` や `list_all_files()` にも当たらない
- パーミッション: `chmod` は一時ファイル側、`.bak` は旧本体の inode なのでモードも旧本体のまま。旧実装（move）と同じ
- 空のファイルは `.bak` に残さない、`skipped_lines`、`_stat_key` の扱いは変わっていない
- テスト 1（`test_save_swap_failure_keeps_original_and_backup`）: 実装を HEAD の版（`shutil.move` だけ）へ戻したコピーで実行し、`FileNotFoundError` で**落ちる**ことを確認した
- `docs/data-format.md` の「バックアップ」の節、`docs/obsidian-format-review.md` の 43 行目は実装と一致している
- `rg -n "退避|\.bak"` と `rg -n "shutil|move\(|移す"` の結果: `save()` の順序を旧版のまま説明している箇所は他に無い（`data-format.md` 100-104 行目は旧形式の経緯を述べた箇所で、対象外）

## 確信度の高い指摘

### 1. テスト 2 件とも、一時リンクを片付ける行を消しても通る

- `src/ytsched/ytsched.py:816` の `link_pathname.unlink(missing_ok=True)` を `pass` に置き換えたコピーでも、`tests/test_ytsched.py` は 198 件すべて通った（実測）
- 理由: テスト 2（`test_save_without_hardlink_falls_back_to_move`）は `os.link` 自体を失敗させるので、一時リンクが作られない。テスト 1 は `except` に入らない
- 問題になる状態: `os.link` が成功し、`link_pathname.replace(.bak)` が `OSError` になったとき。片付けの行が消えても気づけず、`.01.jsonl.bak.<hex>` が残り続ける（旧本体へのハードリンクなので、容量も解放されない）
- なお、テスト 2 は実装を旧版へ戻しても通る。これは fallback の確認なので当然で、指摘ではない

## 確信度の低い気づき（実害は未確認）

### a. `KeyboardInterrupt` などで `os.link` と `replace(.bak)` の間を抜けると、一時リンクが残る

- `except OSError` は `BaseException` を捕まえず、外側の `except BaseException` は一時ファイルしか消さない
- 実測: `replace(.bak)` で `KeyboardInterrupt` を起こすと、`.01.jsonl.bak.<hex>`（本体と同じ inode）が残った。本体は無事
- 隠しファイルで、glob にも当たらないので、残るのはゴミだけ。SIGKILL や電源断でも同じ間に残るので、完全には防げない

### b. 失敗の理由を問わず、黙って `shutil.move` へ移る

- `except OSError` は「ハードリンクが使えない」以外（`EACCES`、`EMLINK`、Linux の `fs.protected_hardlinks` による `EPERM` など）も同じく fallback にする。ログも出さない
- 保存そのものは成功するので実害は無いが、「本体が無い時間」がある経路を通っていることが外から分からない。`debug` でも出しておくかは main の判断
- `docs/data-format.md` 164-165 行目の「ハードリンクが使えないファイルシステムでは」も、実際の条件（`os.link` か `replace(.bak)` が `OSError`）より狭く書いている

### c. `.bak` と同じ名前のディレクトリがあると、本体がその中へ入る（旧実装から変わらない）

- `replace(.bak)` が `IsADirectoryError` → fallback の `shutil.move` が本体を `01.jsonl.bak/01.jsonl` へ移す（実測）。本体は新しい内容で作られる
- 旧実装も `shutil.move` だったので同じ挙動。今回の変更による後退ではない
