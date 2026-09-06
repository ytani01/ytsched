# TODO-191 verifier 報告

## (a) コマンド例が実際に動くか

- `codegraph explore "trash_handler.py"` — ○。`src/ytsched/trash_handler.py`
  の verbatim ソースが行番号付きで返った（`Found 10 symbols across 1 file.`）
- `codegraph query "restore" -l 5" ` — ○。シンボル名・種類・ファイル:行番号・
  シグネチャが 5 件返った（`_restore`, `_restore_id`,
  `test_setLevel_none_restores_default`, `test_restore_keeps_uuid_and_increments_version`,
  `test_restore_adds_new_entry_and_keeps_trash`）

## (b) 「日本語は無視される」という主張

- `codegraph explore "trash"` → `Found 36 symbols across 3 files.`
- `codegraph explore "trash 全然関係ない日本語"` → `Found 36 symbols across 3 files.`
  （一致。主張どおり）
- `codegraph explore "ゴミ箱"` → `No relevant code found for "ゴミ箱"`
- `codegraph explore "予定"` → `No relevant code found for "予定"`
  （主張どおり、日本語だけのクエリは空振りした）

## (c) 行番号の主張

`grep -n "def add_sde\|def save" src/ytsched/ytsched.py`:

```
738:    def save(self):
781:    def add_sde(self, sde: SchedDataEnt) -> None:
1051:    def add_sde(self, date: datetime.date | None, sde: SchedDataEnt) -> None:
1107:    def save(self) -> None:
```

`~/.claude/CLAUDE.md`・`CLAUDE.md`（ytsched）双方の記述
（`add_sde` が 781・1051、`save` が 738・1107）と一致。○

## (d) 追記が CODEGRAPH_START/END の外にあるか

`~/.claude/CLAUDE.md` を確認。`<!-- CODEGRAPH_END -->` は 350 行目で終わり、
「### クエリは英語で書く」の節は 352 行目から始まっている。マーカーの
外側にあることを確認した（○）。

## (e) 書式が周囲と揃っているか

- 見出しレベル: `~/.claude/CLAUDE.md` 側は `###`（`## CodeGraph` の子節として
  自然）。`CLAUDE.md`（ytsched）側は `## CodeGraph` で、既存の他の `##` 節
  （`## ログ` 等）と同じレベル。揃っている
- 箇条書きの形: 両方とも `- **太字の要点。** 説明` の形で、既存の他節
  （例: ytsched CLAUDE.md の「### 文書の確認（wording）」節）と同じ書式
- 行の折り返し幅: 目視で他の段落とおおむね同じ幅（40字強）で改行されており、
  極端に長い/短い行は見当たらなかった

## 結論

依頼にある主張はすべて実際の値と一致した。食い違いは見つからなかった。
