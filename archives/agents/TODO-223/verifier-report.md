# verifier 報告（TODO-223）
1. 取り残し: ○ `rg -n "User\.md" ...` の出力は docs/Developer.md:245 の TODO-152 リンク 1 件のみ
2. リンク先: ○ docs/UsersGuide.md・Install.md・Developer.md 実在（README.md 2 件、Install.md 1 件、Developer.md 1 件の新リンク）。TODO-152 のファイル（%20 を戻して）も実在（test -f）
3. main.html:397: ○ `https://github.com/ytani01/ytsched/blob/HEAD/docs/UsersGuide.md`
4. archives: ○ `git status --short archives` は `?? archives/agents/TODO-223/` のみ。docs/user-*.png 6 件と tools/user-figs.json は名前そのまま（git status に出ない）
差分外の変更なし（README, TODO.md, Developer.md, Install.md, mise.toml, my.css, main.html, annotate.py, User.md→UsersGuide.md の rename）。
