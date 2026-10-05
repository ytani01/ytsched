# TODO-219. 使われていないコードと重複を整理する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Haiku 4.5、定型の実行） |
| 実施 | Opus 5.5 / effort medium | implementer（Sonnet 5.5 / medium）+ reviewer（Opus 5.5 / high）+ verifier（Haiku 4.5、定型の実行） |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 62 | 6,254 | 53,036 | 1,610,488 | 55% |
| implementer | Sonnet 5.5 | medium | 36 | 360 | 122,277 | 482,884 | 20% |
| reviewer | Opus 5.5 | high | 14 | 2,141 | 38,457 | 184,759 | 7% |
| verifier | Haiku 4.5 | 記載なし | 148 | 3,506 | 67,923 | 450,946 | 17% |
| 合計 |  |  | 260 | 12,261 | 281,693 | 2,729,077 | 計 3,023,291 |

- verifier は定義のモデルが sonnet。lint・型チェック・テストを順に走らせるだけなので Haiku 4.5 に上書きした（TODO-203）。Haiku は effort に対応しない
- 集計は `--since '2026-10-05 11:43:00'`（立てた直後の着手だが、始点を着手の時刻にそろえた）

## きっかけ

コード全体を無駄な処理・過剰な実装の観点で見直して、使われていないコードと
重複が見つかった。**挙動は変えない**前提で整理する。

## やったこと

- `src/ytsched/trash.py`: `entries()`・`count()`・`delete_many()` に 3 回あった
  1 行の読み取り（decode → `json.loads` → `trashed_at` の型確認）を `_parse_line()` に、
  捕まえる 4 種の例外を `_BAD_LINE` にまとめた。壊れた行の扱い
  （`entries()`/`count()` は警告して飛ばす、`delete_many()` は元のバイトのまま残す）は同じ
- `TrashFile.delete()` を消し、テストを `delete_many()` に書き換えた。
  戻り値が件数になったので、テスト名の `returns_false` を `returns_zero` に直した
- `SchedDataEnt.get_date()`・`set_date()`・`SchedData.get_keys()` を消した。
  `get_date`/`set_date` のテスト 3 件は消し、`get_keys()` でキャッシュの並びを見ていた
  テスト 2 件は `sd._sdf_cache` を直接見る形に変えた（並びは公開 API では見られない）
- `src/ytsched/ytsched.py` のコメントアウトしたログの行を消した。対になっていた
  `# if not sdf.sde:` の断片と、それで使われなくなった `_i`・`_discarded` も整理した

`click_common_opts()` の `use_h`・`use_d`・`use_v` は**消さない**ことにした。
`click_utils.py` は `mylog.py`（TODO-220）と同じく他のプロジェクトとそろえるため、
書き換えない（利用者の指示）。

## 確かめたこと

- reviewer: `_parse_line()` の文の並び、例外の種類、警告の文言・回数、壊れた行を
  残す扱いが元と同じこと。消したメソッドの呼び出し側が残っていないこと。
  `click_utils.py`・`mylog.py` に差分が無いこと
- verifier: `mise run fmt`・`lint`・`typecheck`・`test` が通った（719 件）

## 残ること

- `entries()`/`count()` の警告の文言と回数は、どのテストでも確かめていない
  （reviewer の指摘。今回は読んで変わっていないことを確かめただけ）

## 分担の振り返り

担当の報告は `archives/agents/TODO-219/` にある。

- **各担当が何を見つけたか。** implementer は 4 項目を実装し、`get_keys()` を
  使うテストの扱いを判断として挙げた。reviewer は要修正なしとしたうえで、
  コメント削除で残った断片・未使用変数・テスト名の食い違いを挙げた（main が直した）。
  verifier は問題を見つけなかった
- **見込みとの食い違い。** 編成は見込みどおり。途中で項目 5 が取りやめになり、
  implementer は一度直した `click_utils.py` を戻した。implementer と verifier が
  `pgrep -f pytest` で終わりを待つループをバックグラウンドで残し、そのループが
  自分自身のコマンド行に当たって終わらなかった（main が kill した）。
  利用者には implementer が動き続けているように見えた
- **次に同じ規模ならどう組むか。** 同じ編成でよい。依頼文には、他のプロジェクトと
  そろえるファイル（`mylog.py`・`click_utils.py`）を「触らないもの」として
  最初から書く。担当には「テストの終わりはフォアグラウンドで待ち、
  `pgrep -f` のループを残さない」と書き添える
