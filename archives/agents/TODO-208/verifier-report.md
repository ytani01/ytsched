# TODO-208 verifier 報告

- ○ `uv run pytest tests/test_trash.py -q` : 24 passed
- ○ `uv run pytest tests/test_web.py -q -k "trash or Trash or undecodable"` : 30 passed, 145 deselected
- ○ 実アプリ: datadir=`mktemp -d`(/tmp/tmp.tZAmCphJJb)、trash.jsonl に有効行1つ + `"title":"\xff"` の行
  - `uv run ytsched webapp --datadir <一時> --port 10199` 起動
  - `curl --max-time 10 -s -o /dev/null -w '%{http_code}'` : /ytsched/ = 200、/ytsched/trash = 200
  - ログに Traceback / Error の出力なし
- アプリは PID 949545 / 949549 を kill で停止（停止後 port 10199 のプロセスなし）

不具合なし。判断が要る点なし。
