# TODO-044 implementer 報告

対象は `tools/token-usage.py` のみ。`.claude/agents/*.md` と
`~/.claude/CLAUDE.md` には触れていない。

## 変更したファイル

- `tools/token-usage.py`

## やったこと

### 1. `collect()` を最大値集計に直した

`(requestId, message.id)` が同じ行が複数出てきたとき、以前は
「先に出会った行」をそのまま使い捨てて後続を無視していた。
`merged: dict[key, Record]` に変え、同じ key に出会うたびに
`output` / `cache_creation` / `cache_read` / `input` の各項目を
`max()` で更新するようにした。`usage.messages` は初回の 1 のまま
（上書きも加算もしない）。

### 2. 概算料金

- `PRICING` に `claude-opus-5` / `claude-sonnet-5` / `claude-haiku-4-5`
  の $/1M 単価を持たせ、`price_for()` で前方一致で引く。表に無い
  モデルは `DEFAULT_PRICING_MODEL`（Opus 5）の単価で数え、警告を出す
  （`_warned_models` で同じモデル名の警告は 1 回だけに抑えた。依頼書に
  厳密な指定は無かったが、実行のたびに同じ警告が何度も出るのは
  ノイズと判断した）
- `record_cost()` で 1 レコードごとに `output・input・cache_creation
  （input の 1.25 倍）・cache_read（input の 0.1 倍）` から料金を出し、
  `collect()` の最後にまとめて `Record.usage.cost` へ入れている
  （max 集計が終わったあとの最終値に対して計算するため）
- `Usage` に `cost: float` を足し、`add()` でも合算する。これで
  `sum_by()` / `total_of()` は今までどおり `usage.add()` を呼ぶだけで
  料金も一緒に集計される
- Sonnet 5 の単価コメントに「2026-08-31 までの導入価格」と明記した

### 3. 出力

- `Usage.main_total`（`output + cache_creation`）は削除し、割合・
  並び順はすべて `cost` を基準にした（`sum_by()` のソートキー、
  `fmt_shares()` の分母）
- `print_summary()` を依頼どおり 2 行に分けた
  （`消費: output … / cache_creation … / 概算 $…` と
  `main NN% + …（料金の割合）`）。`（参考: cache_read …）` はそのまま
- `print_table()` に `$` 列を追加。`担当` の表・`モデル` の表どちらにも
  出る

## 確かめたこと

- `mise run fmt` / `typecheck` / `test` … すべて成功（418 件 pass、
  lint・型チェックとも指摘なし）
- `git stash` で変更前後を切り替えて `uv run python
  tools/token-usage.py TODO-043` を実行し、数字の変化を確認した
  - 変更前: `verifier` の `output` は 654（依頼書どおり）
  - 変更後: `verifier` の `output` は **1,176**
    （TODO-044 の見込みに書かれていた「2,000〜3,000 程度になるはず」
    という目安には届かなかったが、途中経過ではなく最終値を拾うように
    直した結果として増えている。実測値なので、見込みとの差はそのまま
    報告する）
  - 概算料金は合計 `$5.3`。担当ごとの割合は `main 71% + verifier 25%
    + wording 3% + runner 0%`。TODO.md の背景にある「料金で見ると
    reviewer/wording の比率が小さくなる」という傾向どおり、消費の
    行（旧: output+cache_creation ベース）の割合と料金ベースの割合が
    ずれていることを確認した
- `uv run python -c "..."` で `price_for()` を単体で呼び、前方一致・
  未知モデルへのフォールバック・警告が 1 回だけ出ることを確認した
- `--list` も問題なく動作することを確認した

## 単独で決めた判断

- **未知モデルの警告を 1 回だけに抑えた。** 依頼書には「警告を出す」
  としか書かれておらず、複数回出すかどうかの指定は無かった。同じ
  モデル名で何十件もレコードがあると警告が埋め尽くすと判断し、
  `_warned_models` という module レベルの集合で重複を抑えた
- **料金は `Record` 単位で計算し、`collect()` の最後（max 集計が
  終わったあと）にまとめて入れる形にした。** 途中経過の行にまで
  料金を計算すると、max 集計で捨てられる値のぶん無駄になるため

## 直さずに残したもの（範囲外）

- `.claude/agents/verifier.md` の絞り込みと `implementer.md` の
  読み方の追記は、依頼どおり main が別に行うため触っていない
  （`git status` で見ると既に変更が入っていた）
- `~/.claude/CLAUDE.md` に消費の行の実測値を残す作業は、TODO-044 の
  「決めたこと」に「この項目ではやらない」と明記されているので
  何もしていない
