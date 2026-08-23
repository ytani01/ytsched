# TODO-029. コードレビューで見つかった 3 件を直す

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer
実施: main = Sonnet 5 → Opus 5（途中で切り替え）/ effort high、担当 = implementer + verifier + reviewer

分担の理由と各担当の報告は
[`archives/agents/TODO-029/`](../agents/TODO-029/) にある。

- [x] 移行のときに行末の `\r` を落とす
- [x] 編集画面の `orig_date` を、その行が入っているファイルの日付にする
- [x] 検索・フィルタ文字列を `normalize()` に通す

## きっかけ

TODO-021 までの変更（`src/` 全体）を `/code-review` にかけて出た 3 件。
どれも JSON Lines へ移した（TODO-018・TODO-020）ときに入ったもので、
テストは 330 件とも通っていた。

1. **移行のときの `\r`。** CRLF の旧 `.cgi` を `ytsched migrate` にかけると、
   各行の最後のフィールド（`detail`）の末尾に `\r` が残ったまま `.jsonl` へ
   書かれる。旧形式ではテキストモードの `readlines()` と `text2htmlstr()` の
   `replace("\r", "")` で消えていたので、移行で新しく入るもの
2. **`date` が食い違う行。** `edit.html` が `orig_date` に行側の日付を出す
   ので、`fix` したときに `cmd_del()` が別の日のファイルを見に行って空振り
   し、`cmd_add()` が表示していた日のファイルへ書く。結果は重複
3. **検索・フィルタ文字列の正規化。** 照合される側の
   `SchedDataEnt.search_str()` は `normalize()` を通るのに、入力側は
   `.lower()` しかしていない。`会議（重要）` を `（重要）` で検索しても
   当たらなかった

## やったこと

| ファイル | 要点 |
| --- | --- |
| `src/ytsched/migrate.py` | `Migrator.conv_file()` で、行ごとに末尾の `\r` を落としてからデコードする |
| `src/ytsched/edit_handler.py` | `orig_date`（読み込んだファイルの日付）を作って `render()` へ渡す |
| `src/ytsched/main_handler.py` | `cmd=update` の `render()` にも `orig_date` を渡す。`search_str` / `filter_str` の変換を `normalize()` に揃える |
| `src/ytsched/webroot/templates/edit.html` | `{% set orig_date = … %}` を消す |
| `docs/data-format.md` | 正規化の段落を書き直し。移行の手順に「行末の `\r` は落とす」を追記 |
| `src/README.md` | フィルタ・検索文字列の扱いと、`EditHandler` の `orig_date` の説明 |

### 1. `\r` は `split_lines()` ではなく `migrate.py` で落とした

`SchedDataFile.split_lines()` は `.jsonl` の読み込みでも使われ、飛ばした行は
生のバイト列のまま `skipped_lines` に入って `save()` が書き戻す決まりに
なっている（`docs/data-format.md`「壊れた行の扱い」）。ここで `\r` を落とすと
読み込み側の仕様まで書き直すことになるので、影響が移行だけで閉じる
`Migrator.conv_file()` の側で `raw_line.removesuffix(b"\r")` した。

**行の途中の `\r` は残す。** 旧実装ではその `\r` で行が割れていたので、
どのみち結果が違う。TODO-029 の範囲（行末）を超えるため手を付けていない。

### 2. `orig_date` は handler が決める

テンプレートで `sde.date` から作るのをやめ、`EditHandler.get()` と
`MainHandler.exec_cmd()` が「その行を読み込んだファイルの日付」を渡す。
読み込みの方針（行の `date` を信じる）は変えていないので、表示上の日付との
食い違いはそのまま残る。

**新規（`sde_id` 無し）のときは表示している日付にした。** `None` にすると、
新規の編集画面で `fix` を押したときに `cmd_del(None, …)` が `ToDo.jsonl` を
開いて `.bak` まで作る道が開く。

### 3. 入力側も `normalize()` に通す

`search_str` は `convert=str` ＋ `.lower()` から、`filter_str` は
`convert=str.lower` から、どちらも `convert=normalize` へ。全角括弧は
半角になる ＝ 正規表現のグループとして解釈されるので、リテラルとして
書きたいときは `\(` と打つ必要がある（`docs/data-format.md` に書いた）。

`get_conf_arg()` は変換後が文字列なら変換後を保存するので、`search_str` も
`Conf.cgi` へ正規化後が入るようになった（`filter_str` と揃った）。

## テスト

402 件（着手前は 392 件）。`ruff format --line-length 78` / `ruff check` /
`basedpyright` / `mypy` も通っている。verifier が別途、一時ディレクトリで
サーバと `migrate` を動かして 3 点とも実地で再現した
（[`verifier-report.md`](../agents/TODO-029/verifier-report.md)）。

挙動を変えたので、TODO-021 で足した
`test_search_str_is_saved_as_is_and_shown_lowered` の 1 件が落ちた。
新しい挙動に合わせて `test_search_str_is_saved_normalized` へ書き直した。

## reviewer の指摘と、その扱い

[`reviewer-report.md`](../agents/TODO-029/reviewer-report.md)。
`src/` の変更には正しさの問題は見つからず、判断 2 点（1 の落とす場所、
3 の `Conf.cgi` への保存）はどちらも妥当という見立てだった。
指摘はテストと文書に 3 件で、**すべて直した**。

- **常に通るアサーション。** `assert all("\r" not in json.dumps(d) …)` は、
  `json.dumps()` が CR を `\r` の 2 文字へエスケープするので、値に CR が
  入っていても必ず通る。値そのものを見る形に直した。同じ理由で、
  implementer の報告にある「`od -c` で確認」も確認になっていなかった
  （修正自体は `detail` の値を見る assert が担保している）
- `test_crlf_empty_line_is_skipped` は変更前でも通る（`is_empty_line()` が
  `strip()` を使うため）。**挙動が変わっていないことの確認**だと分かるよう
  docstring に書き足した
- `src/README.md` の `orig_date` の説明に、新規のときの分岐を書き足した

確信度が低いものとして挙がった 3 件のうち、`MainHandler.exec_cmd()` の
`orig_date` が実質 no-op である件は、テンプレートから handler へ寄せる意味は
あるのでそのままにした。残り 2 件は TODO-034 へ回した。

## 据え置きだったものの決着

TODO-028 の reviewer から据え置かれていた 2 点。

- **`get_conf_arg()` の保存方針。** `search_str` も `normalize()` になって
  「文字列を返す変換はすべて変換後を保存する」に揃ったので、**挙動としては
  片付いた**。`isinstance(converted, str)` で実行時に決める設計そのものは
  変えていないが、揃った以上わざわざ書き換える理由も無いので、
  **これで閉じる**
- **`SchedDataFile.date2path()` の `expanduser()` が 2 か所に分かれている**
  件は手つかず。TODO-034 へ回した
