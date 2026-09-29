# TODO-210 定型の実行 報告

## 1. uv run ruff format --check --line-length 78 src tests tools
- 終了ステータス: 0
- 結果: ✓ **通過**
- 出力: `42 files already formatted`

## 2. uv run ruff check --extend-select I src tests tools
- 終了ステータス: 0
- 結果: ✓ **通過**
- 出力: `All checks passed!`

## 3. uv run basedpyright src tests tools
- 終了ステータス: 0
- 結果: ✓ **通過**
- 出力: `0 errors, 0 warnings, 0 notes`

## 4. uv run mypy src tests tools
- 終了ステータス: 0
- 結果: ✓ **通過**
- 出力: `Success: no issues found in 39 source files`

## 5. uv run pytest tests -q
- 終了ステータス: 0
- 結果: ✓ **通過**
- 実行時間: 144.62秒（約2分24秒）
- 出力: `712 passed in 144.62s`

## 6. 動作確認（SchedDataFile ハードリンク実装）

### テスト内容
- 一時ディレクトリで `SchedDataFile` を使用
- 予定を 1 件追加して `save()`
- もう 1 件追加して `save()`
- その後、ディレクトリの状態、行数、inode/nlink を確認

### 確認結果

**(a) 日付ディレクトリ内容**
```
  30.jsonl
  30.jsonl.bak
```
✓ 結果: `.` で始まる一時ファイルなし

**(b) 行数**
```
Main file: 2 lines
.bak file: 1 lines
```
✓ 正常。最初の `save()` で 1 行、次の `save()` で 2 行

**(c) inode と nlink**
```
Main file:
  st_ino:   442384
  st_nlink: 1
.bak file:
  st_ino:   442383
  st_nlink: 1
```
✓ 別 inode（ハードリンク未使用）
✓ 両方とも nlink = 1

## 結論
すべての確認が正常に完了。TODO-210 の実装は正常に動作しています。
