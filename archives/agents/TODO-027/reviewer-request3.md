# TODO-027 reviewer への依頼（3 回目）

2 回目に出た指摘 1（`month`/`day` の `OverflowError`）・2（更新経路の
`date`/`orig_date`）・3（`EditHandler` の `date`）に対応した実装が
終わった。**直り方を見てほしい。コードは直さないこと。**

**注意: この項目の変更はまだコミットされていない。**
`git checkout` / `git restore` / `git stash` など、**作業ツリーを戻す
コマンドは絶対に使わないこと**（3 回目の implementer が
`git checkout -- src` で未コミットの実装を一度消している）。
`git diff` / `git status` は読むだけなので構わない。

## 読むもの

- `archives/agents/TODO-027/reviewer-report2.md`（2 回目の指摘）
- `archives/agents/TODO-027/implementer-request3.md`
- `archives/agents/TODO-027/implementer-report3.md`
- 変更そのものは `git diff`

## 特に見てほしいところ

1. **指摘 1・2・3 が本当に直っているか。** **まだ 500 になる経路が
   残っていないか**。実装者は `get_time_arg()`（`time_start=abc`）が
   手つかずだと申告している。ほかにもあるか
2. **`orig_date` が読めないときに「消さない」ことにした判断**
   （実装者の報告「単独で決めた判断」の 1）。
   - `cmd=fix`/`update` で**同じ `sde_id` の予定が 2 つ残る**という
     副作用を実装者自身が申告している。**これは、消えるより本当に
     ましか。** 「コマンドごと無視して何も書かない」（消しも足しも
     しない）ほうがよくないか。**あなたの見立てを書いてほしい**
   - `orig_date_is_broken` を `get_argument()` の二度読みで作っている
     形は妥当か。もっと素直な形があるか
3. **`HandlerBase` へ上げた判断**（`convert_value()` / `date_range()` /
   `check_date()` / `str2date()` / `SEARCH_MODE_MAX_DAYS`）。
   - `SEARCH_MODE_MAX_DAYS` が `HandlerBase` にあるのは自然か
     （検索は `MainHandler` の話）。継承で読めるとはいえ、置き場所が
     ずれていないか
   - `check_int_range()` の使い手が `MainHandler` だけなのに
     `HandlerBase` にある件
   - **`src/README.md` の `HandlerBase` の説明が「`Conf.cgi` の読み書き」
     のままになっている。** 直すべきか（直すならこの項目の中で）
4. **`day` を 1..31 で先に弾く形が、日付の正しさの判断を変えていないか。**
   月末（2 月 31 日など）は `datetime.date()` に任せていると書いてある。
   `day=32` の警告文だけが変わることの是非
5. **足したテスト 13 件**が挙動を固定するものになっているか。特に
   `TestInvalidUpdateArgs` が「消し間違いが起きない」ことを本当に
   押さえているか
6. **3 回目の implementer が `git checkout -- src` で未コミットの実装を
   一度消し、控えから書き戻している。** `git diff` を読んで、
   **1・2 回目の実装が欠けていないか**を確かめてほしい（2 回目の
   あなたの報告に書いた `date_range()` / `check_date()` /
   `str2date()` / `str2todo_days()` / `str2ymd_date()` が、
   `HandlerBase` への移動を差し引いてそのまま残っているか）

## 決まりごと

- コードは直さない
- 報告は `archives/agents/TODO-027/reviewer-report3.md` に書く。
  **直っているものは「直っている」と明記する**
- 返事は 5 行以内
