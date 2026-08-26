# TODO-057 verifier 報告

読んだ順: `TODO.md` の TODO-057 → `request-implementer.md` →
`implementer-report.md` → `reviewer-report.md` → `implementer-report-2.md` →
`request-verifier.md`（追記含む）→ `git diff`。

## fmt/typecheck/lint/test

```
mise run fmt      # ruff format: 25 files left unchanged / ruff check: All checks passed!
mise run typecheck # basedpyright: 0 errors, 0 warnings, 0 notes / mypy: Success: no issues found in 22 source files
mise run lint      # 上記2つと同じ
mise run test      # pytest: 439 passed in 3.07s
```

すべて OK。`upgradeproject` は走らせていない。

## キャプチャ（変更前後）

`git worktree` で `HEAD` を `/tmp/todo057/wt_before` に出し、`--datadir` を分けて
2 つ起動（前: port 10086、後: port 10085、`--datadir` は空の一時ディレクトリを
新規作成）。`mise run shot` 相当（`tools/screenshot.py`）で 412px/800px を撮影。
`compare -metric AE` で差分を取ったところ、現在の日付セル内に 1 箇所だけ diff
（`diff412.png`）があったが、拡大して見比べると見た目は同一で、ブリンク
カーソルのタイミングによる偶発的なピクセル差と判断（TODO-057 の変更とは無関係）。
それ以外は完全に一致。**静止画は変更の前後で同じに見える → 期待どおり**。
置き場所: `/tmp/todo057/shots/`（`before_*` / `after2_*` / `diff412.png` など）。

## 画面での動きの確認（playwright + 合成 TouchEvent）

CDP の `Input.dispatchTouchEvent` は、この環境では touchmove の座標が実際の
指定値と一致せず（同じ値に固まる・順序が入れ替わるなど）信頼できなかった
（`/tmp/todo057/touch_test*.py` で再現・切り分け）。代わりに、ページ内で
`new Touch()` / `new TouchEvent()` を組み立てて `window.dispatchEvent()` する
方式に切り替えたところ、安定して動いた（`/tmp/todo057/full_test.py`）。
また `is_mobile=True` を付けると viewport が無視される不具合があったため、
`has_touch=True` のみ指定（`is_mobile` は外した）。

1. **指に追従**: OK。`translateX(-60px)`→`-150px` と連続して動いた
2. **送りの判定**: OK（3 パターンとも）。1/3 以上ゆっくり→送られる
   （`date=2026-08-26`→`08-31`）。1/3 未満ゆっくり→戻る（URL 不変、
   transform が空文字に戻る）。60px でも速く払うと送られる
3. **縦スクロール**: OK。40 件の予定を入れた縦長の週で `scrollY` が
   `0`→`64` に変化
4. **縦スクロール中のスワイプで隣週が上下にずれない**: OK。スクロール後、
   ドラッグ中の `.my-week-cur` / `.my-week-next` の `getBoundingClientRect().top`
   が、ドラッグ前と一致（ズレ無し）
5. **スワイプ・◀▶・←→ のどれでも動く**: OK。いずれも `date=2026-08-26`から
   正しく前後の週（`08-31`/`08-24`）に遷移
6. **ホームボタン（今日から離れた週）**: OK。`date=2026-01-05` から
   ホームを押すと `date=2026-08-26`（今日を含む週）へ遷移し、`my-week-cur`
   パネルが存在（TODO-049 の退行なし）
7. **検索モードで見た目・動きが変わらない**: OK。`.my-week-panel` が
   `my-week-cur` の 1 つだけ
8. **検索欄で文字を選ぼうとしても週が変わらない**: OK。`#search_str` 上で
   横ドラッグしても URL は不変

## とくに見てほしい 2 点（追記の 2・3 点目）

- **◀▶ 連打で送りが 1 回ずつ正しく進むか**: `page.click()` を 50ms 間隔で
  3 回叩く方式では、実際のページ遷移（≒100ms 前後で完了。ヘッドレス環境
  では CSS `transition: 0.2s` より速く終わることを実測）を挟むため、DOM
  要素が張り替わってクリックが 1 回取りこぼされる現象があった（3 回で
  `09-07` 止まり、期待は `09-14`）。これは実際の連打ではなく、テスト環境
  でのクリックとナビゲーションの競合と判断し、**`moveToMonday()` を同じ
  `page.evaluate()` 内で 2 回・3 回、完全に重ねて直接呼ぶ**方法で確認し
  直したところ、`onloadHdr`（ページ読み込み）は毎回ちょうど 1 回だけ発火し、
  最終 URL も 1 回分だけ進んだ正しい日付になった（`overlap_test.py` /
  `overlap_test3.py`）。`cancelActiveSlide` により古い呼び出しの
  `on_done()`（`doGet()`）が呼ばれないことを確認できた
- **送り終えたときに元の週へ巻き戻って見えないか**: コードは
  `finish()` が `transform` をリセットせずに `on_done()` を呼ぶ形に
  なっており、`cancelSwipeDrag()`（戻すときだけ）が別にリセットする
  作りであることを `git diff` で確認した。動的な確認は、ヘッドレス環境で
  `touchend` からページ再読み込みまでが約 100ms と短く、`MutationObserver`
  で `style` 属性の変化を記録しようとしても実行コンテキストが途中で
  破棄され、確実な連写・記録ができなかった。**「巻き戻って見えるか」の
  実機に近い確認は、この環境ではできなかった**
- **検索モードで余白が見えないか**: OK。`hasAdjacentWeek()` が false のため
  `#week_wrap` の `transform` はスワイプ中・後とも空文字のまま変化せず、
  余白も生じない

## console / サーバログ

一連の操作で console の error は 0 件。`touch.log`・`after.log`・
`before.log` に例外・トレースバックなし（起動ログのみ）。

## 判断が要る点

- **巻き戻り（1 点目）は、この環境では実機に近い形で確認しきれなかった。**
  コード上はリセットしない作りになっているが、視覚的な検証は積み残し
- キャプチャ・テストスクリプトは `/tmp/todo057/` に置いた（リポジトリは汚していない）
