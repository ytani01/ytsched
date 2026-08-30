# TODO-126 verifier への依頼

## 目的

`ytsched holiday` サブコマンド（TODO-126）の実装が実際に動くかを確かめる。
仕様は `TODO.md` の「## TODO-126.」の節。実装の報告は
`archives/agents/TODO-126/implementer-report.md`。

対象: `src/ytsched/holiday.py`、`src/ytsched/__main__.py`、
`tests/test_holiday.py`、`tests/data/syukujitsu-sample.csv`

## 確かめること（これだけ。思いついた確認を足さない）

1. `mise run lint` が通る
2. `uv run pytest tests` が通る（全体）
3. `uv run ytsched holiday --help` が出る。年を渡さずに
   `uv run ytsched holiday --datadir <一時ディレクトリ>` を叩くと
   **エラーになる**（0 で終わらない）
4. **一時ディレクトリ**を `--datadir` に指定して、`--url` に
   `file://<絶対パス>/tests/data/syukujitsu-sample.csv` を渡し、
   次の順で実際に叩いて結果を目で見る:
   - `--dry-run` で 2026 → ファイルが 1 つも作られないこと
   - `--dry-run` 無しで 2026 → `2026/01/01.jsonl` などができ、
     中身の `type` が `休日`、`title` が CSV のまま（`元日`）、
     `time_start` / `time_end` が null であること
   - もう一度同じコマンド → 全部「飛ばした」に数えられ、
     予定が二重に増えないこと（`.jsonl` の行数を before/after で見る）
   - CSV に無い年（`2030`）を混ぜて `2026 2030` → 2030 は
     「データが無い」と報告され、他の年の処理は続くこと
5. **本物のネットからの取得が動くか**を 1 回だけ確かめる。
   一時ディレクトリを `--datadir` に、`--url` は既定のまま、
   **`--dry-run` を必ず付けて** `uv run ytsched holiday 2026` を叩く。
   件数が出て、例外・トレースバックが出ないこと
   （ネットに出られない環境なら、その旨を報告に書いて飛ばしてよい）

## 絶対にやらないこと

- **`~/ytsched/data` を `--datadir` に指定しない。** 必ず一時ディレクトリ
- **コードを直さない。** 見つけたことは報告するだけ
- `mise run upgradeproject` は走らせない

## 報告

`archives/agents/TODO-126/verifier-report.md` に、叩いたコマンドと
結果（出力の要点）、見つかった問題を書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。
