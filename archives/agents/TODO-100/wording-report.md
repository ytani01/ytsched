# TODO-100 wording 報告

対象は依頼のとおり 7 ファイル（TODO.md の差分、archives/todo の 1 件、
archives/agents/TODO-100 の README・依頼書 2 件・報告 2 件）。

前例の有無は `git grep -cF <語> HEAD -- '*.md'` で確認した（基準は HEAD、
このコミット前の状態）。

## 前例の無い語

### 到達経路（0 件）

- 箇所: `verifier-report.md` 末尾「不具合」節
  「到達経路が無いため、対応するかどうかは main の判断に委ねる。」
- 前例: 0 件（`到達しない` は 6 件あるが `到達経路` という名詞化は無い）
- 見立て: 「そのコードパスに至る呼び出し経路が無い」という意味で使って
  いて、文脈上は通じる。ただし「到達しない」で言い換えられ、わざわざ
  名詞化する必要は無さそうに見える。このリポジトリだけの言い換えの
  可能性がある

### 素直なほう（0 件）

- 箇所: `implementer-request.md` 5 行目
  「`Path` に統一するか、実装側で素直なほうを選んでよい。」
- 前例: 0 件
- 見立て: 「（コードとして）自然・簡潔なやり方」という意味で使っている
  と思われるが、「素直な実装」「素直なほう」という言い回しは一般に通用
  するかどうか判断できない。曖昧さも残る（何を基準に「素直」と判断する
  かが書かれていない）

### タイミングのぶれ（0 件）

- 箇所: `implementer-report.md`「自分で確かめたこと」節
  「パス関連の変更とは無関係なタイミングのぶれと判断した」
- 前例: 0 件（「ぶれ」単体、「タイミング」単体は探していないが、
  この組み合わせでの前例は無い）
- 見立て: 「実行タイミングに依存する不安定な結果」という意味で、
  一般に通用しそうな言い回し。テストの flaky な失敗を指しており、
  このリポジトリ独自の造語というよりは普通の日本語に見える

### 既知の件（0 件）

- 箇所: `verifier-report.md` 47〜50 行目
  「implementer 報告の『気づいたが直していないこと』に既に書かれている
  既知の件」
- 前例: 0 件
- 見立て: 「既知の事項」「既知の問題」の言い換えとして自然で、一般に
  通用しそうに見える。ただし「件」を単独で名詞のように使う点は、この
  リポジトリの他の文書での使われ方（「N 件」のような助数詞）とは
  少しずれており、判断できない

## 前例があり、問題なさそうな語（参考）

以下は候補に挙がったが前例が複数あり、造語ではないと判断した。

- 波及（4 件）、到達しない（6 件）、判断したこと（11 件）、
  黙って無視（2 件）、残骸（12 件）、挙動（420 件）、対象外（57 件）、
  正規化（45 件）、揃える／揃えた（101／59 件）、
  自分で確かめたこと（38 件）、気づいたが直していないこと（2 件）、
  うまくいかなかったこと（1 件）

## 読んだファイル

- `/home/ytani/work/ytsched/TODO.md`
- `/home/ytani/work/ytsched/archives/todo/TODO-100. os.path を pathlib へ移す.md`
- `/home/ytani/work/ytsched/archives/agents/TODO-100/README.md`
- `/home/ytani/work/ytsched/archives/agents/TODO-100/implementer-request.md`
- `/home/ytani/work/ytsched/archives/agents/TODO-100/implementer-report.md`
- `/home/ytani/work/ytsched/archives/agents/TODO-100/verifier-request.md`
- `/home/ytani/work/ytsched/archives/agents/TODO-100/verifier-report.md`

## 前例の無い語数

4 語（到達経路、素直なほう、タイミングのぶれ、既知の件）
