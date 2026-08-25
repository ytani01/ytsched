# TODO-054 verifier 報告

## 1. 決まった手順

```
mise run fmt
mise run typecheck
mise run lint
mise run test
```

- `ruff format`: 25 files left unchanged
- `ruff check`: All checks passed!
- `basedpyright`: 0 errors, 0 warnings, 0 notes
- `mypy`: Success: no issues found in 22 source files
- `pytest`: 430 passed in 3.02s

いずれも OK。`mise run upgradeproject` は走らせていない。

## 2. 実際に動かす

`--datadir` は一時ディレクトリ（`/tmp/.../scratchpad/data`）、ポートは
18054。`uv run ytsched webapp --port 18054 --datadir <一時ディレクトリ>`
で起動し、HTTP 200 を確認（`/ytsched/`・`/ytsched/edit/` とも）。
`{{ }}` `{%` の生残りは無し。

playwright（scratchpad の venv に別途インストール）＋ CDP
`Input.dispatchTouchEvent` で、`/usr/bin/chromium` を
`env -u DISPLAY` 付きで操作。`has_touch=True, is_mobile=True` の
コンテキストで、2026-08-24〜28 週にダミー予定を置いて確認した。

結果（すべて `#cur_day` で判定、OK）:

- 左へ払う→次週（2026-08-26 → 08-31）／右へ払う→前週（→08-24）
- 縦優勢（dx=90, dy=280〜400）→変化なし
- 横 60px 未満（dx=40）→変化なし
- 画面左端（x<30px）・右端（x>幅-30px）から開始→変化なし
- 800ms 超（hold 1000ms）→変化なし
- 検索欄（`#search_str`）上から開始→変化なし
- ピンチ（2 本指）→週は変化なし。**ただしブラウザ自体がピンチズーム
  する**（`visualViewport.scale` が 1→3.58 に変化。`touch-action` や
  `user-scalable=no` の指定が無いため、モバイルブラウザの既定動作。
  アプリのコードの不具合ではなく、この文書内の依頼の範囲外の挙動として
  報告しておく）
- ゲージの針: `el.style.bottom`（JS が代入した瞬間の値）ではなく
  `getBoundingClientRect().top` で描画位置を追ったところ、遷移直後の
  約 140ms から 360ms あたりまで連続的に値が変わり（220.5px →
  229.8 → 238.1 → 245.5 → 254.5 → 258.7 → 261.2 → 261.5px で収束）、
  0.3 秒程度かけて動くことを確認した
- 縦スクロール: viewport を 412×500 にして `body_h=750 > win_h=500`
  の状態を作り、縦スワイプで `scrollY` が 0→250 に変化することを確認
  （`passive` 登録によりスクロールが妨げられていない）
- 上記の一連の操作で、console の error/warning は 0 件。サーバの
  `webapp.log` にも例外・トレースバックは出ていない（起動ログのみ）

### テスト中に見つけた挙動（コードの不具合ではない、報告のみ）

一連のテストを 1 ページ（同一 `BrowserContext`）内で連続して行うと、
ピンチ操作の直後に行った「もう一度左へ払う」スワイプが**週を送らなく
なる**現象に遭遇した。原因を追ったところ、アプリ側の判定ロジックの
問題ではなく、**ピンチでブラウザが実際にピンチズームしてしまい、
以降の絶対座標 (`clientX`/`clientY`) 基準のスワイプが、ズーム後は
別の要素（今回は「予定を追加」ボタン）に当たってしまっていた**ことが
原因だった。ページを再読み込みしてズームを解除すれば通常どおり動く。
アプリの不具合ではないので、コードは直していない。

## 3. 編集画面ではスワイプが効かないこと

`/ytsched/edit/?date=2026-08-26` で左スワイプを送っても URL は変化せず
（`2026-08-26` のまま）、`main.html` だけに登録されている想定どおり。

## 判断が要る点

- 上記「ピンチでブラウザがズームする」件は、依頼の確認項目
  （週が変わらないこと）自体は満たしているので不具合ではないが、
  **実機で意図せずピンチズームしてしまう体験は起こり得る**。
  `touch-action` や `user-scalable=no` を入れるかどうかは、
  TODO-054 の範囲か、別項目にするかの判断が main に要る。
