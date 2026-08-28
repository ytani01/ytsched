# TODO-092 wording 報告

そのコミットに入る `.md` を、既知語リストを持たずに読み、`HEAD` を基準に
前例の有無を数えた。文書は直していない。

## 読んだファイル

- `archives/todo/TODO-092. テンプレートの掃除.md`（新規）
- `archives/agents/TODO-092/README.md`（新規）
- `archives/agents/TODO-092/implementer-report.md`（新規）
- `archives/agents/TODO-092/verifier-report.md`（新規）
- `TODO.md`（差分。TODO-092 の節を削除し、完了済みの目次にリンク 1 行を追加。
  追加分に新しい語は無い。削除された節にあった「色分け」「期限の近さ」は
  `HEAD:TODO.md` に残っているので前例あり扱い）

## 前例の無い語（`git grep -cF <語> HEAD -- '*.md'` が 0 件）

いずれも 0 件なので、独自の言い換えに見えるものから並べる。

### 独自の言い換えに見えるもの

- **検索期間バー**
  - `archives/todo/TODO-092. テンプレートの掃除.md:54`
    「`main.html` の検索期間バーの `{% set days = ... %}`」、同 `:70`
    「検索期間バーは `(in 1826 days)` と表示」。
    `archives/agents/TODO-092/verifier-report.md:36` にも。
  - 前例なし（`検索バー` は TODO-048 に 2 件）。
  - 見立て: `main.html` の「検索期間を示すバー表示」を指す臨時の呼称。
    コード上の正式名ではない。UI 部品の説明としては通じる。

- **生テンプレートタグ**
  - `archives/todo/TODO-092. テンプレートの掃除.md:70`
    「生テンプレートタグの残りなし」。
    `archives/agents/TODO-092/verifier-report.md:34,36`
    「生テンプレートタグ 0 件」。
  - 前例なし。
  - 見立て: 「展開されずに残った `{{ }}` / `{% %}`」の意。説明的だが
    このリポジトリ独自の言い回し。過去の報告では「未展開の `{{`」
    （implementer-report.md:73 でも同じ表現）や「生の `{{ }}`」が使われている。

- **背景クラス**
  - `archives/todo/TODO-092. テンプレートの掃除.md:18`
    「期限の近さで背景クラスを分ける判定」。
  - 前例なし。
  - 見立て: 「背景色を決める CSS クラス」の縮め方。通じるが独自。

### 一般に通用しそうなもの・新規コード識別子

- **`todo_urgency` / `_urgency` / `TODO_NEAR_DAYS` / 戻り値 `over` `near`**
  - `archives/todo/TODO-092. テンプレートの掃除.md:32-35`、
    `archives/agents/TODO-092/README.md:24-26`、
    `archives/agents/TODO-092/implementer-report.md:16-18,30-31,41`。
  - いずれも前例なし。
  - 見立て: この項目で追加したコードの識別子（メソッド名・クラス定数・
    戻り値）。文書上の造語ではない。ただし「urgency（緊急度）」という
    概念名をこのリポジトリで初めて使う点は記しておく。判断は main。

- **名前空間共有**
  - `archives/agents/TODO-092/implementer-report.md:13`
    「名前空間共有のため `{% set %}` の位置を動かすと壊れる」。
  - 前例なし（`名前空間` 単独は TODO-083 等にあり）。
  - 見立て: Tornado の `{% include %}` が親と名前空間を共有する挙動の
    呼称。技術的に妥当な複合語。

- **Tornado コメント**
  - `archives/agents/TODO-092/implementer-report.md:11`
    「1 行目直後に Tornado コメント `{# ... #}` を追加」。
  - 前例なし（`Tornado` 単独は複数）。
  - 見立て: `{# ... #}`（Tornado テンプレートのコメント構文）を指す。
    妥当な呼び方。

- **セクションコメント**
  - `archives/agents/TODO-092/implementer-report.md:51`
    「セクションコメント `# date / cur_day / ...`」。
  - 前例なし。
  - 見立て: ソース中の区切りコメントを指す一般的な言い方。

- **色分け判定**
  - `archives/agents/TODO-092/implementer-report.md:16`
    「ToDo の色分け判定（旧 13〜20 行）」。
  - 前例なし（`色分け` は `HEAD:TODO.md` の TODO-092 節に 1 件）。
  - 見立て: 普通の日本語の複合語。

- **生きた参照**
  - `archives/agents/TODO-092/implementer-report.md:57`
    「`delta_day1` に生きた参照が 1 つあった」、
    `archives/todo/TODO-092. テンプレートの掃除.md:55`「生きた参照だった」。
  - 前例なし。
  - 見立て: 「まだ使われている参照」の意。"live reference" 相当で
    一般に通じる範囲。

- **死んでいるもの**
  - `archives/agents/TODO-092/README.md:30`
    「K で消すのは死んでいるものだけ」。
  - 前例なし（`死んだコード` は TODO-003 等、`死んだ属性` は TODO-003）。
  - 見立て: 「デッドコード」の口語的な言い換え。通じる。

- **掃除前 / 掃除後**
  - `archives/agents/TODO-092/README.md:20,21`、
    `archives/todo/TODO-092. テンプレートの掃除.md:29`。
  - 前例なし（`掃除` は TODO-049 等）。
  - 見立て: 項目名「テンプレートの掃除」を前後で受けた語。普通の日本語。

- **生き残り**
  - `archives/agents/TODO-092/implementer-report.md:74`
    「死んだ属性（...）の生き残りなし」。
  - 前例なし。
  - 見立て: 「消し残し」の意の口語。普通の日本語の範囲。

## 参考（構成語は既出なので挙げない）

- 「タイミング依存の flaky」— `タイミング依存` は TODO-003、`flaky` は
  TODO-049 に前例あり。連結句としては初出だが問題視しない。

## まとめ

- 前例の無い語: **12 項目**（`todo_urgency` 系の識別子群を 1 つと数えて）。
  目安の 10 語を超える。ただし内訳は、新規コード識別子と一般的な日本語が
  大半で、実質的に独自の言い換えに見えるのは **検索期間バー / 生テンプレート
  タグ / 背景クラス** の 3 語。
- 直すかどうか、識別子名の扱いは main が判断。
