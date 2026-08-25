# TODO-049 verifier 報告

## 1. 決まった手順

```
mise run fmt
mise run typecheck
mise run lint
mise run test
```

すべて green。

```
[fmt] ruff format: 25 files left unchanged / ruff check: All checks passed!
[typecheck] basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success: no issues found in 22 source files
[test] 430 passed in 3.19s
```

## 2. 実際に起動して見た

`uv run ytsched webapp --port 18199 --datadir <一時ディレクトリ>` を
バックグラウンドで起動し、`mkdata.py` で作ったダミーデータ（今日=2026-08-26
中心の23日分 + ToDo5件）を読ませて確認した。playwright（システムの
chromium、`env -u DISPLAY`）で操作した。

- **週の範囲。** `?date=2026-08-26`（水）で 08/24(月)〜08/30(日) の
  7 欄ちょうど。それより前後の欄は無い。○
- **週送り。** メニューの `#forward_button` / `#back_button` を 3 回ずつ
  押し、08/24週 → 08/31週 → 09/07週 → 09/14週 → 戻って元の 08/24週。
  日付がずれていかないことを確認。○
- **キーボード ←→。** `ArrowRight` を 2 回押して 08/31週 → 09/07週へ
  正しく進むことを確認。○
- **今週へ戻る（ホーム）。** 1 回押しで戻ることを確認。さらに
  週送り→ホーム 2 回押しでも同じ今週（08/24週）に戻ることを確認。○
- **ゲージの針。** 今週は針 (`#gage_r` の `bottom`) と基準線
  (`#gage_r_base`) がどちらも `490px` で完全に重なる。
  +1週=428px、+2週=408px、+3週=397px、戻すと 428px→490px と対称に
  戻る。週を送るたびに前の週の位置から動いて見える
  （`sessionStorage` の仕掛けどおり）。○
- **検索。** `search_str=健康` で送ると縦一覧（`date-` ブロックが 2 件、
  週表示のような 7 件固定ではない）が出る。一覧の日付
  （`onmousedown="doPost(..., {date: '2026-05-18', ...})"`）を押すと
  `?date=2026-05-18` へ 302 で飛び、その日を含む週
  （05/18〜05/24）の週表示に切り替わることを確認。○
- **編集。** 予定の追加ボタン→タイトル入力→保存（`fix`）で、
  `?date=2026-08-24&modified_sde_id=...` へリダイレクトし、
  追加した週（08/24週）がそのまま表示され、本文に
  `verifier-test-event` が入っていることを確認。削除・修正は
  試していない（追加のみで手順を確認した）。○
- **ブラウザの戻る/進む。** 保存後の一覧から `go_back()` で編集画面
  （`/ytsched/edit/?date=2026-08-24&sde_id=`）へ、`go_forward()` で
  一覧（`?date=2026-08-24&modified_sde_id=...`）へ、それぞれ正しく
  戻ることを確認。○
- **JavaScript のコンソール。** 上記の一連の操作
  （週送り3回×2方向・キーボード2回・ホーム2種・検索・検索結果クリック・
  編集追加・戻る/進む）を通して `page.on("console")` で拾った
  error/warning は 0 件。○
- **サーバのログ。** 上記操作の間、例外・トレースバックは出ていない
  （`INFO webapp.py:114 main()> start server: run forever ..` 以降、
  他のログ行なし）。○
- **HTML にテンプレートの残骸が無いこと。** `{{`/`{%` の生の残りは
  無し。○

補足: 検索モードの `search_str` は `conf.json` に永続化されるので、
週表示側の確認をする前に `?search_str=` で一度クリアしてから見た
（実装の挙動どおりで、不具合ではない）。

## 3. キャプチャ

`mise run shot` 相当（`tools/screenshot.py`、幅 412px と 800px）で撮影。
`~/tmp/playwright-mcp/` に保存。

- `after-thisweek_closed_412.png` / `after-thisweek_closed_800.png`
  （今週、08/24〜08/30）
- `after-nextweek_closed_412.png` / `after-nextweek_closed_800.png`
  （`?date=2026-09-02` で送った次の次の週、08/31〜09/06）
- `after-search_closed_412.png` / `after-search_closed_800.png`
  （`?search_str=健康` で検索したあと、縦一覧）

見た目は、7 日ぶんの日付ブロックが縦に並び、今週はゲージの針が
基準線に重なり、次週は `+1w` 付近まで下がっていることを画像で確認した。

## 確かめられなかったもの

- 依頼書にある「編集の削除・修正」までは行わず、追加のみ確認した
  （手順自体は追加と同じ手順なので、必要なら追加で見る）
- iOS Safari 実機での確認は行っていない（TODO-054 のスワイプの範囲）
