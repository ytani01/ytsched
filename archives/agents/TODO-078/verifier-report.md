# TODO-078 verifier 報告

## 1. lint / pytest

- `mise run lint`：ruff format / ruff check / basedpyright / mypy すべて問題なし
- `uv run pytest tests -q`：459 件 pass。skip なし
  （`test_browser.py` の 19 件も込みで実行されている）

## 2. 見え方の比較（変更前後）

`git worktree add <一時dir> HEAD`（HEAD = TODO-077 まで。TODO-078 は未コミット
の作業ツリーだったため、旧版は `HEAD`、新版はいまの作業ツリー）でそれぞれ
`uv run ytsched webapp --datadir <一時dir> --port` を別ポートで起動し、
`tools/screenshot.py` で撮って見比べた。

- 目盛り 14 個（`-30y` 〜 `+30y`）の文字と位置：旧版・新版でスクリーン
  ショットが一致（画像参照）
- 針の上の文字（`#gauge_r_label`）：今週で両方とも `±0`
- 画像:
  - 旧版: `/tmp/claude-649/-home-ytani-work-ytsched/fa0a069c-4a3f-4345-bb88-af5ffd0e2834/scratchpad/old_shot.png/shot_closed_800.png`
  - 新版: `/tmp/claude-649/-home-ytani-work-ytsched/fa0a069c-4a3f-4345-bb88-af5ffd0e2834/scratchpad/new_shot.png/shot_closed_800.png`

## 3. 週の移動・読み込み直後・遠い週の直接表示

playwright で新版のみ確認（旧版は今回変えていない挙動なので比較不要と判断）。

- `?date=2027-05-10`（今週から離れた週）を直接開いても、目盛り 14 個・
  針の上の文字（`+8.5m`）とも読み込み直後から出ていた。
  画像: `/tmp/claude-649/-home-ytani-work-ytsched/fa0a069c-4a3f-4345-bb88-af5ffd0e2834/scratchpad/new_far.png/shot_closed_800.png`
- キーボード（`ArrowRight`）で週を送ると `#gauge_r_label` が `±0` → `+1w` に
  正しく変わった
- 検索（`search_str` に文字を入れて Enter）すると、ゲージの帯（`.my-gauge-bar`
  ごと）が非表示になり、目盛りは 0 個（＝帯が出ていないので目盛りも出ない）。
  余計な残骸は見えなかった。
  画像: `/tmp/claude-649/-home-ytani-work-ytsched/fa0a069c-4a3f-4345-bb88-af5ffd0e2834/scratchpad/new_search.png`

（スワイプ／ゲージのタップ操作は今回試していない。JS のロジックは
`dispGauge()` 経由で共通なので、キーボード操作の確認で代替したが、
未確認である旨をここに書いておく）

## 4. HTML の書き残し

`curl` で新版のトップページを取得し、`{{` `{%` を grep：ヒットなし。
`.my-gauge-label` の要素はテンプレートには残っておらず、コメントのみ。

## 5. サーバログ

新旧とも `error` / `exception` / `traceback` の文字列なし。

## 総評

依頼書の確認項目はすべて期待どおり。不具合は見つからなかった。

## main の判断が要る点

- スワイプ操作・ゲージのタップ操作は実機/playwright のタッチイベントで
  試していない（キーボード操作のみ確認）。必要なら追加で確認する
