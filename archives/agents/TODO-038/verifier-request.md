# TODO-038 verifier への依頼

TODO-038（HTML・CSS のリファクタリング）の変更が、**見た目を変えずに
入っているか**を確かめてほしい。

## 何が変わったか

作業ツリーに未コミットで入っている。3 段階に分けて実装した。

1. [1 段目の依頼](implementer-request-1.md) /
   [報告](implementer-report-1.md) — 重複した id・使われていない CSS と JS
   を消す、`const detail_h` → `let`、`doPost()` の引数に引用符
2. [2 段目の依頼](implementer-request-2.md) /
   [報告](implementer-report-2.md) — `style` 属性を CSS のクラスへ寄せる、
   `{% if sde.is_canceled() %}` の繰り返しを 7 → 3 か所に
3. [3 段目の依頼](implementer-request-3.md) /
   [main の覚書](main-note-step3.md) — 値をそのまま名前にしたクラスの
   付け直し。**3 段目の implementer は検証に入る直前に落ちたので、
   確認が一切取れていない。ここがいちばん厚く見てほしいところ**

## 比べる相手

`HEAD`（コミット `cca8269`、TODO-037 が済んだ状態）と、いまの作業ツリー。
`git archive HEAD src/ytsched/webroot | tar -x -C <一時ディレクトリ>` で
旧版を取り出し、**2 つのサーバを別ポートで立てて同じ画面を撮り、
`compare -metric AE` で数える**。2 段目の implementer が同じやり方で
やっていて、報告に手順が書いてあるので参考にすること。

## 確かめてほしいこと

### 1. 画素単位の比較（いちばん重要）

- 一覧・編集を、少なくとも **412 幅と 740 幅**の両方で
- **データに次を全部入れること。**入れないと今回いじった分岐を通らない
  - 普通の予定 / **重要（★）の予定** / **取り消しの予定**（`x` と `(欠`）
  - 祝日 / ToDo（期限が **過去 / 1 週間以内 / 先** の 3 通り）
  - 場所ありの予定 / 詳細が複数行の予定
  - **今日の日付ブロック**と、平日・土日が全部出る日付の範囲
- 詳細を開いた状態、メニューを開いた状態も見ること
- 検索した画面も見ること

### 2. 既に分かっている差 1 件（これは差が出てよい）

**取り消し済みの予定の「詳細」を開いたときだけ、上下の空行が 2 行ずつ
減る**（普通の予定と同じ見え方になる。1 行の詳細で欄の高さが
122px → 62px）。利用者が了承済み。

**これ以外の差が出たら、全部報告すること。** 1 画素でも報告してよい。

### 3. 3 段目で特に怪しいところ

- `edit.html` の場所の行から `<span class="my-fs-large">@</span>` が
  **`<span>` ごと外されて `@` だけになっている**。親の行が `large` なので
  同じはず、という判断だが、確認が取れていない
- `edit.html` の種別の行で、`my-fs-large` が `col` から `row` へ移った
  （`.my-edit-row`）。継承で同じはず、という判断
- Bootstrap 4.5 のクラスへ置き換えた 20 か所。**Bootstrap 側はどれも
  `!important` が付いている**（`.align-middle` `.align-bottom` `.d-none`
  `.font-weight-bold`）。自前の定義には付いていなかったので、
  他の宣言に勝つようになった可能性がある
- 重要（★）の太字が `.font-weight-bold`（`700!important`）になった。
  元は `font-weight: bold`

### 4. そのほか

- `mise run lint` / `mise run test`
- **一時ディレクトリ**を `--datadir` に指定して起動し、一覧・編集・検索が
  200 で返ること
- ブラウザの JavaScript の例外が出ないこと（一覧・編集 × 412 / 740）。
  `chromium --headless --dump-dom --enable-logging=stderr` で見られる
  （Playwright は入っていない）

## 環境の注意

- **ポート 12345 で利用者が `ytsched` を動かしている。止めないこと**
- 起動には **10097 と 10098** を使う。使い終わったら止めること
- `pkill` はパターンで自分のシェルを巻き込む。`pgrep` で PID を
  確かめてから kill すること
- **`~/ytsched/data` は絶対に使わない**（`--datadir` に一時ディレクトリ）
- `mise run upgradeproject` は走らせない
- 一時ファイルは `/tmp/claude-649/-home-ytani-work-ytsched/1aabf7d9-2054-4095-8cae-087382f1b160/scratchpad/` の下に置くこと

## 決まりごと

- **コードは直さない。** 見つけたことは報告するだけ
- **`TODO.md` は編集しない。git commit もしない**
- 報告は
  `/home/ytani/work/ytsched/archives/agents/TODO-038/verifier-report.md`
  に**絶対パスで**書き、返事は 5 行以内で
