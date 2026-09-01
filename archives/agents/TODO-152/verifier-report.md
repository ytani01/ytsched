# TODO-152 verifier 報告

## 1. lint / pytest

- `mise run lint`（ruff format / ruff check / basedpyright / mypy / eslint / prettier）… ○ すべて通過
- `uv run pytest -q` … ○ 597 passed（162.44s）

## 2. PNG の健全性

`identify docs/user-*.png` … ○ 6 枚とも壊れていない（PNG, 1524px 幅で統一）。

```
docs/user-edit.png    1524x1282
docs/user-menu.png    1524x526
docs/user-month.png   1524x1710
docs/user-search.png  1524x1180
docs/user-trash.png   1524x868
docs/user-week.png    1524x1886
```

## 3. 参照とリンク

- `docs/User.md` は 6 枚すべてを `![...](user-*.png)` で参照している（week / edit /
  month / menu / trash / search）。パスは相対で、ファイルは実在する。切れていない
- `docs/Developer.md` は `[../archives/todo/TODO-152. docs/User.md に画面図を入れる.md]`
  を参照。**ただしこのファイルはまだ存在しない**（`archives/todo/` は
  TODO.md 側の項目が決着したときに main が作るもの）。verifier の時点では
  リンク切れだが、これは TODO-152 が決着した時点で main が作るファイルなので、
  実装側の不具合ではない（判断材料として報告のみ）

## 4. 図の中身（目視）

6 枚とも Read ツールで開いて確認。吹き出しの画面外はみ出し・文字切れは無し。
引き出し線は概ね指し示す先に届いている。

- `user-search.png` だけ、左側の 3 本の引き出し線（「いま出ている結果より…」
  「さかのぼった一番古い日」「押すと、その週へ移って…」）が互いに交差していて
  少し追いにくいが、指している先自体はそれぞれ合っている（虫めがねボタン／
  06/17 の行／同じ 06/17 の行）。実害というほどではないので不具合とはせず、
  気になる点として書いておく

## 5. 本文と実装の食い違い

- 編集画面のボタン説明（戻る／更新／完了／複製／削除）は
  `src/ytsched/webroot/templates/edit.html` の `data-cmd` の並び
  （back → update(sync) → fix(check-square) → add(clone, `not new_flag` のときだけ)
  → del(trash)）と、`MainHandler.exec_cmd()` の挙動（`update` は編集画面に
  留まる、`fix`/`add`/`del` は週表示側へ戻る）に一致している。○
- 検索結果の説明（擬似図を消したあと）… 「探し始めた日」「目標件数」
  「もっと前を探す」ボタンの挙動など、`user-search.png` の吹き出しに
  対応する本文がある。○ 不足なし

## 6. `tools/annotate.py` の動作確認

一時ディレクトリで webapp を起動し（後述）、`week` の画面を 1 枚撮って確認。

```
uv run python tools/annotate.py --srcdir <shots> --only user-week -o <out>
→ saved: .../user-week.png（1 枚だけ生成）
uv run python tools/annotate.py --srcdir <shots> --only no-such-name -o <out2>
→ その名前の図が無い: ['no-such-name']  / exit=1
```

○ どちらも依頼どおりの挙動。

## 7. 実データに触れていないこと

- `uv run ytsched webapp --datadir /tmp/.../scratchpad/vdatadir --port 10186` で起動
- `curl http://localhost:10186/ytsched/` → 200
- `find ~/ytsched/data -newer CLAUDE.md` … 変更されたファイル無し。○
- 確認後、起動した webapp プロセスは kill 済み

## 判断が要る点

- `docs/Developer.md` が指す `archives/todo/TODO-152. ....md` は、この時点では
  まだ存在しない（TODO.md 側の決着作業で main が作る想定）。verifier からは
  リンク切れに見えるが、実装側の不備ではないと判断した
- `user-search.png` の左側の引き出し線 3 本が交差していて見た目がやや窮屈。
  実害は無いので不具合としては扱っていないが、直すなら `tools/user-figs.json`
  の左側の吹き出し位置を調整する必要がある
