# verifier 報告 TODO-240

一時 datadir + `uv run ytsched webapp --port 10299`、Playwright（412px、/usr/bin/chromium）。実データ不使用。
最初に `git status`: 依頼外の変更なし（TODO.md・model-check.md・docs 2 つ・reviewer-report.md）。

1. ○ PNG+txt を一度に選び「完了」→ 開くと a.png が表示（naturalWidth 1）、b.txt はリンク。
   b.txt は `Content-Disposition: attachment; filename*=UTF-8''b.txt`、a.png は `inline`。
2. ○ 内容が空で添付だけ: 閉じたとき「添付 2 件」（画像は出ない）、開くと「添付 2 件」+ b.txt。
3. ○ 同名 b.txt を付け直すと `b-1.txt`。「外す」に印→更新で b-1.txt が消えた。
4. ○ 複製: 新しい予定に添付なし、元の添付フォルダは増減なし。
5. ○ 削除後ゴミ箱 3 件。1 件完全削除→フォルダ残る。2 件目まで→残る。最後の 1 件→フォルダごと消えた。
6. ○ 「3.1 添付ファイル」→ GitHub 規則で `31-添付ファイル`。目次と一致（読んだだけ）。

食い違い: なし。サーバログに Traceback なし。作業ツリーのソースは書き換えていない。
