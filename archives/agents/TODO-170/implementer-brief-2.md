# TODO-170 implementer への依頼（2 回目・レビュー指摘の反映）

1 回目の実装（`src/ytsched/fix_id.py`）に対して、reviewer と verifier の
報告が出た。verifier の確認では不具合ゼロ（実データのコピーで
6555 ファイル・13418 行を書き換え、`sde_id` 以外の不一致 0 件）。
reviewer の指摘のうち、main が「直す」と決めた 4 点だけを反映する。

reviewer の報告: `archives/agents/TODO-170/reviewer-report.md`

## やること

1. **末尾の改行は、補う現状の振る舞いのままにする**（利用者が決めた）。
   コードは変えない。代わりに:
   - `fix_file()` の docstring（またはモジュールの docstring）に
     「元のファイルが改行で終わっていなくても、書き戻したファイルは
     必ず改行で終わる」と明記する。理由（JSON Lines は改行で終わるのが
     正しい形で、`SchedDataFile.save()` も必ず改行を付ける）も添える
   - テストを 1 つ足して、この振る舞いを固定する
     （末尾に改行が無いファイルを書き換えると改行が付く）
2. `src/ytsched/fix_id.py:129` の
   `except UnicodeDecodeError, json.JSONDecodeError:` に**括弧を付ける**
   （`except (UnicodeDecodeError, json.JSONDecodeError):`）。
   動作は変わらないが、Python 2 の構文と誤解されるのを避ける
3. 使われていない `_log = getLogger(__name__)`（`fix_id.py:43`）を**消す**。
   モジュール直下でログを出していないため。クラス内の `__log` は残す
4. **空行を「読めなかった行」に数えない。** いまは本文中の空行が
   `json.loads("")` で `JSONDecodeError` になり `lines_unreadable` に
   入る。`SchedDataFile.is_empty_line()` を使って空行は別に扱い、
   **行はそのまま書き戻したうえで、`lines_unreadable` には数えない**
   （`SchedDataFile.load()` が空行を警告もカウントもしないのに合わせる）。
   件数の出力に空行の行を足すかどうかは任せる（足すなら
   `FixIdStat` に項目を 1 つ増やし、`main()` の出力にも出す）

## テストの追加（境界値。reviewer が手薄だと指摘した）

- 末尾に改行が無いファイル（上の 1）
- 空ファイル
- 本文中に空行があるファイル（空行が残り、`lines_unreadable` に
  数えられない）
- 複数行のうち末尾の行だけが JSON として読めないファイル

## やらないこと

- 上の 4 点以外は変えない。**動く実装をむやみに書き直さない**
- 文書（`docs/`・`README.md`）は writer が別に書く。触らない
- `TODO.md`・`archives/` は main が書く。触らない
- **`~/ytsched/data` の実データには絶対に触らない**

## 完了条件

- `mise run fmt` / `typecheck` / `lint` / `test` が通る
  （`mise run upgradeproject` は走らせない）
- 一時ディレクトリのデータで `ytsched fix-id` を自分でも叩いて、
  件数の出力が変わっていないことを確かめる

## 報告

`archives/agents/TODO-170/implementer-report-2.md` に書く。返事は 5 行以内。
