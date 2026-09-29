# TODO-209 implementer 報告

## 変更
- src/ytsched/conf.py: DEF_CONF の ToDo_Days を "365"、コメントも直した
- src/ytsched/holiday.py: urlopen に timeout=30
- src/ytsched/ytsched.py: sdf_has_sde() 削除（rg で src/tests に他の呼び出し無しを確認済み）
- src/ytsched/webroot/templates/base.html: autoescape 1 行削除
- tests/test_handler.py: "1y" -> "365"、DEF_CONF 一致は int(...) == DEF_TODO_DAYS
- tests/test_web.py: "1y" -> "365"（2 か所）
- tests/test_ytsched.py: test_sdf_has_sde* 3 件削除
- src/README.md: CLI 5 コマンド、load_month_cal() の説明、autoescape の節
- docs/data-format.md: 390 行付近は「autoescape None なので」の因果だけ削除
  （旧形式でブラウザが 1 回デコードしていた事実は残した）。446 行付近は
  エスケープされる前提に書き直し

## 結果
- fmt: 42 files left unchanged / lint: ruff・basedpyright 0 errors / typecheck: mypy Success
- test: 712 passed
- rg autoescape src/ytsched/webroot/templates: 0 件

## rg 'autoescape|sdf_has_sde|"1y"' の残り（直さなかった理由）
- main_binder.py:96 "1y": 画面の選択肢なので指示どおり残す
- TODO.md: 編集禁止
- CLAUDE.md:27: 「base.html の autoescape」は src/README.md の節名への案内で、節は残っている
- src/README.md:483,486: 書き直した節そのもの
- docs/web-framework-review.md, image-attach-proposal.md, obsidian-format-review.md,
  code-review.md: 過去のレビュー・提案なので指示どおり直さない

## 判断が要る点
- data-format.md 390 行付近: autoescape が実際は効いていなかったので、旧形式で
  「ブラウザが 1 回デコードした」理由は本当は別にある可能性がある。
  因果の説明だけ外し、事実の文は残した。
