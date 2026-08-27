# TODO-080 reviewer 報告

## 確信度の高い指摘

### 1. `test_get_sdf_no_reload_right_after_save` が、狙った回帰を検出できない

`src/ytsched/ytsched.py` の `SchedDataFile.save()` に足した
「書いたあとに `_stat_key` を持ち直す」処理（654〜656 行）を外しても、
このテストは **落ちない**。

理由: `sd.add_sde(DATE1, mk_sde())` の内部で `get_sdf(DATE1)` が呼ばれた
時点では、まだファイルが無いので `_stat_key = None` になる
（`SchedDataFile.load()` の `FileNotFoundError` 経路）。`sd.save()` で
ファイルが新規にできたあと、`_stat_key` を持ち直す処理を外すと
`_stat_key` は `None` のまま残る。

テストの `sdf1 = sd.get_sdf(DATE1)`（最初の呼び出し）は、この時点で
`is_stale()` が `None != (mtime, size)` で「変化あり」と判定し、
**新しい `SchedDataFile` を作って読み直す**。ただし読み直した内容は
直前に保存したものと同じなので、`sdf1` は正しい中身を持った別インス
タンスになるだけで、テストからは区別が付かない。

`mock.patch.object(sdf1, "load", ...)` は、この**最初の呼び出しのあと**
に取り付けているため、無駄な読み直しが起きたかどうかを見られていない。
2 回目の `sd.get_sdf(DATE1)` は、1 回目で読み直した `sdf1` の
`_stat_key` がすでに正しく更新されているので、当然もう読み直さない。
`sdf2 is sdf1` も `load.assert_not_called()` も、この処理を外した状態で
そのまま通る。

（実際にコードを書き換えて確かめようとしたが、reviewer は書き込み禁止
のため許可されなかった。上のトレースは手で追ったもの。念のため、
`mock.patch.object` を `sd.add_sde()` の直後・`sd.save()` の直前に
差し替えて確かめるよう、verifier か main に依頼することを勧める）

このテスト自体を直せとは言わない（直すのは main の判断）が、
「実装を戻すと落ちるか」という観点では、狙いを外していると考える。

## 確信度は高いが、実害は無いことを確認した点（メモ）

### 依頼書の項目 1（`_dirty_sdf` との噛み合わせ）は問題無し

`add_sde()`/`del_sde()`/`save()` は、`main_handler.exec_update()` の中で
必ず `cmd_del()`・`cmd_add()` のあと `finally: self._sd.save()` が同期的に
実行される（`main_handler.py` 1136〜1152 行）。ハンドラに `async`/`await`
は無く（`grep` で確認済み）、`exec_update()` の中で `get_sdf()` が
再び呼ばれる経路も無い。したがって、`_dirty_sdf` に載った未保存の
`SchedDataFile` を `get_sdf()` が横から差し替えて捨てる、という道は
アプリの通常経路には無い。外部プロセス（`ytsched migrate` など）が
リクエスト処理中のごく短い区間にちょうど書き込む、という理論上の
競合は残るが、単一ユーザ向けアプリの前提では現実的でない。

### 依頼書の項目 4（`DEF_CACHE_SIZE` のコメント）は算数が合っている

`main_handler.months2weeks(24) == round(24*30/7) == 103`、
`SEARCH_MODE_MAX_DAYS == 1825` を実際に確認した。コメントの
「207 週 × 7 日 + ToDo 1 件 = 1450」「検索モードは 1825 まで開きうる」
「大きいほうに合わせて 2000」は、実装（`main_handler.py`）の値と合っている。

ただし、`implementer-report.md` の「変更したファイル」「決めたこと」の
節は「20000 → 1500」「1450 ではなく 1500 にした」と書いてあり、
実際のコードの値（2000）と食い違っている。「気づいたが直していない
こと」の節も「検索モードは範囲外として書いておく」としているが、
実装のコメントは検索モードの 1825 を明示的に取り込んで 2000 を選んで
おり、報告の記述と実装が一致していない。コード自体は正しく見えるが、
報告書が実装の最終状態を反映していない（見直しの経緯が report に
反映されないまま出された可能性がある）。

### 依頼書の項目 2・3 は問題無し

`is_stale()` の `(mtime, size)` の組と `None` の扱いは、ファイルが
無い→できた、ある→消えた、の両方向で正しく動く（テストの
`test_get_sdf_reads_file_created_later` / `test_get_sdf_survives_file_removed`
が実際にその経路を通る）。`save()` の `_stat_key` の持ち直しは、
`with open(...) as f:` の単一ブロックの末尾に置かれており、空ファイルを
書く場合・`skipped_lines` がある場合も含めて分岐なしに同じ経路を通る。

## `~/.claude/CLAUDE.md`・`CLAUDE.md` の決まりからの逸脱

無し（`mylog` のラッパ使用、ログの出し方、TODO の範囲、いずれも
問題は見当たらなかった）。
