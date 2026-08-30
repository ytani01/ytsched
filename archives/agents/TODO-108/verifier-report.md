# TODO-108 verifier 報告

- ○ `.venv/bin/pytest tests/test_web.py -q`: 126 passed（3.03s）。
- × `.venv/bin/pytest tests/test_browser.py -q`: 2 回とも 30.2 秒後に途中のドット出力だけで終了し、passed/failed の完了結果を得られなかった。終了後に `pgrep -af pytest` で pytest 本体は残っていないことを確認した。
- ○ `mise run lintjs`: ESLint 成功。
- ○ `mise run webapp -- --datadir /tmp/ytsched-todo108-verifier --port 10108` を起動し、`curl -sS -o /tmp/todo108-main.html -w '%{http_code}\\n' http://127.0.0.1:10108/ytsched/` と `curl -sS -o /tmp/todo108-edit.html -w '%{http_code}\\n' 'http://127.0.0.1:10108/ytsched/edit?date=2026-08-30'` はともに 200。
- ○ 取得 HTML を `rg -n '\\{\\{|\\{%'` と `rg -n ' on[a-zA-Z]+='` で検索し、ともに該当なし。`rg -o 'data-action="[^"]+"'` では main/edit の data-action を確認。
- ○ 停止時は `pgrep -af 'ytsched webapp --datadir /tmp/ytsched-todo108-verifier'` で PID 3259972, 3259974, 3259977 を確認し、3259972、続けて 3259974 を PID 指定で kill。再確認で該当なし。

## 判断が必要な点

ブラウザテスト全体の完了結果を得られていないため、これを成功として扱うか、別の実行環境で再実行するかの判断が必要。
