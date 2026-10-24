# TODO-222 reviewer の報告

対象: ytsched の未コミット差分（`notify.py` / `__main__.py` /
`tests/test_notify.py` / `docs/User.md` / `docs/Developer.md`）と、
`~/work/slack-send` の未コミット差分（`slack-send.sh` / `README.md`）。

要修正: 無し。

## 検討

### 1. タイトルに `` ` `` があると、予定の行のインラインコードが崩れる

- 場所: `src/ytsched/notify.py` の `build_schedule_section`
  （`` line = f"  `{slack_escape(line[2:])}`" ``）
- 内容: タイトルが `` a`b`c `` の予定は `` `a`b`c` `` になり、Slack では
  インラインコードが途中で切れ、`b` は地の文として出る（出力は実測、Slack で
  どう見えるかは未確認）。`ponytail:` のコメントで限界として書いてあり、
  意図して見送ったものと読める。ただし `TODO.md` の注意にも文書にも書かれて
  いない。今のまま進めるなら、そう決めたことを項目の記録に残すかどうかを
  main が決める。実害は未確認

### 2. `--url` に `?` `|` `>` を含む値を渡すとリンクが壊れる

- 場所: `src/ytsched/notify.py` の `build_schedule_section`
  （`f"<{url}?date={date.isoformat()}|{header}>"`）
- 内容: URL の値はそのまま差し込まれる。実測の出力:
  - `https://e.net/?a=1` → `<https://e.net/?a=1?date=2026-09-02|...>`
    （`?` が 2 つになり、`date` が正しく渡らない）
  - `https://e.net/a|b` → `<https://e.net/a|b?date=...|...>`
    （最初の `|` で区切られ、表示が `b?date=...` になるはず）
  - `https://e.net/a>b` → `<https://e.net/a>b?...>`（リンクが途中で閉じる）
- 渡すのは cron を書く利用者本人なので、実際に起きる可能性は低い。
  `docs/User.md` は「Web 画面の URL」としか書いておらず、クエリ文字列を
  付けない前提が文書に無い。実害は未確認

### 3. CLI の `--url` が `build_notify_text` まで渡ることを見るテストが無い

- 場所: `src/ytsched/__main__.py` の `notify`（`url=url`）、
  `tests/test_notify.py`
- 内容: テストはすべて `build_notify_text` を直接呼ぶ。`__main__.py` の
  `url=url` を消しても、テストは 1 本も落ちない。`notify` コマンドの他の
  オプションも CLI 経由のテストは元から無いので、今回の差分だけの抜けでは
  ない。verifier の CLI 実測で補われるなら足りる

## 確信度の低いもの

- **ToDo とメモの行は `` ` `` で囲まないので、`*` `_` `~` が Slack の書式に
  なる。** 例: タイトルが `*todo*` の ToDo は太字で出るはず。mrkdwn には
  これらをエスケープする手段が無いので、直すなら囲むしかない。TODO.md は
  「予定の行を囲む」としか言っておらず、範囲としては今の実装で合っている。
  Slack での見え方は未確認
- **時刻もタイトルも無い予定（タイトルが空）は `` `` `` になる。**
  Slack では文字のまま `` `` `` と出る可能性がある。タイトルが空の予定を
  作れるかどうかも含め、未確認

## 問題なしの観点

- `--url` 無しの出力: 分岐はすべて `if url` の側だけに入っており、既定の
  出力は変わらない。`url=""` を渡しても既定の出力と同じになることを実測した。
  既存のテストが既定の出力を文字列ごと固定している
- エスケープ: `&` を先に置き換えており、順序は正しい。メモ・予定・ToDo の
  3 か所に漏れなく掛かっている。見出し（日付と曜日）には特別な文字が入らない
- slack-send の jq フィルタ: `-r` 無しの payload が変更前と同じ文字列になる
  ことを、`"` `$` `` ` `` `\` `<|>` を含む本文で実測した。`$TEXT_FILTER` は
  二重引用符の中で 1 回だけ展開され、中身の `` ` `` や `$title` が
  シェルに再解釈されることは無い。`getopts` と usage にも `-r` が入っている
- `~/bin/slack-send.sh` はリポジトリへのシンボリックリンクなので、文書の
  cron の例はそのまま `-r` 付きで動く
- テストの強さ: エスケープの順序を逆にする、ToDo かメモのエスケープを外す、
  見出しのリンクを外す、のどれでも `test_url_links_header_and_quotes_lines`
  が落ちる（差分を読んで判断。壊して走らせてはいない）
- 文書と実装: `docs/User.md`・`docs/Developer.md`・slack-send の `README.md`
  の説明は実装と合っている。`docs/User.md` には TODO 番号が入っていない

## 作り込みすぎ

作り込みすぎ: なし（`build_todo_section` の `url` は真偽値としてしか
使わないが、呼び出し側と揃えた形で、削れる行は無い）。

net: -0 lines possible.
