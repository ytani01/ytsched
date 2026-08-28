# TODO-093 wording 報告

そのコミットに入る `.md` 6 ファイルを読み、`HEAD` を基準に前例を数えた。
前例の無い語は 5 語。いずれも 10 語を大きく下回り、造語の疑いは低い文書。
実質的に main の目を通したいのは「seed」1 語。

## 語ごと（前例の少ない順）

### 1. seed

- 箇所:
  - `archives/agents/TODO-093/implementer-brief.md:47`
    「### 3. `main-page.js` — 読み込み時に seed し、`#date_from` を読むのをやめる」
  - `archives/agents/TODO-093/implementer-report.md:19`
    「`ytState.activeMonday = ytState.elWeekWrap.dataset.monday;` を seed。」
- `git grep -icF seed HEAD -- '*.md'`: 前例なし（「シード」も前例なし）
- 見立て: プログラミングで一般的な用語（初期値を与える）で、造語ではない。
  ただしこのリポジトリの `.md` では英語のまま使うのは初出。同じ動作を
  TODO-093 本文・依頼書の他の箇所では「入れる」「移す」「種としての値」と
  和語で書いており、`seed` だけ英語のまま浮いている。表記を合わせるかは
  main の判断。

### 2. 種としての値

- 箇所: `archives/todo/TODO-093. ….md:26`
  「`data-monday="{{ date_from }}"` を付けた。サーバが渡す種としての値は
  ここだけに残す。」
- `git grep -icF 種としての値 HEAD -- '*.md'`: 前例なし
- 見立て: 「種」(seed) 単体はリポジトリ全体で多用（`docs/data-format.md`
  ほか多数）。その一般的な用法の範囲内で、造語というほどではない。判断は
  main。

### 3. 3 重持ち

- 箇所: `archives/agents/TODO-093/implementer-report.md:6`
  「`#cur_day` / `#date` / `#date_from` の 3 重持ちをやめた」
- `git grep -icF "3 重持ち" HEAD -- '*.md'`: 前例なし
  （「3 重」は `archives/agents/TODO-018/verifier-report-2.md` に 1 件）
- 見立て: 同じ値を 3 か所に持つこと、の普通の複合語。造語ではないと思う。

### 4. 弱い手がかり

- 箇所: `archives/todo/TODO-093. ….md:42`
  「`cur_day` はサーバ側で `date` が無いときの弱い手がかりで、数日ずれても
  検索結果はほぼ変わらない」
- `git grep -icF 弱い手がかり HEAD -- '*.md'`: 前例なし
  （「手がかり」単体は TODO-007・TODO-026 ほかに前例あり）
- 見立て: 「手がかり」に「弱い」を添えた普通の日本語。造語ではない。

### 5. 1 本化 / 1 本化し

- 箇所:
  - `archives/todo/TODO-093. ….md:40`「今回の 1 本化で」
  - `archives/agents/TODO-093/implementer-report.md:5`
    「`ytState.activeMonday` に 1 本化し」
- `git grep -icF "1 本化" HEAD -- '*.md'`: 前例なし。ただし「一本化」は
  `archives/todo/TODO-008 / TODO-009 / TODO-092` に前例あり（漢数字か
  算用数字かの違いだけ）
- 見立て: 実質的に既出の語。造語ではない。

## 読んだファイル

- `TODO.md`（ステージ済みの差分。TODO-093 の節を archives へ移す変更）
- `archives/todo/TODO-093. 表示中の週の月曜日の日付を DOM から ytState へ移す.md`
- `archives/agents/TODO-093/implementer-brief.md`
- `archives/agents/TODO-093/implementer-report.md`
- `archives/agents/TODO-093/verifier-brief.md`
- `archives/agents/TODO-093/verifier-report.md`

## 前例なしの語数

5 語（seed / 種としての値 / 3 重持ち / 弱い手がかり / 1 本化）。
うち 4 語は既出の語の変種か普通の日本語。main の目を通したいのは
英語のまま浮いている「seed」1 語。
