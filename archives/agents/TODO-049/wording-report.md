# TODO-049 wording 報告

対象は依頼にある 8 種類・計 14 ファイル（`TODO.md`、
`archives/todo/TODO-049. 1 画面 1 週間の表示にする.md`、
`archives/agents/TODO-049/` の README・依頼書 5 本・報告 5 本、
`src/README.md`）。実際の変更は `git status` / `git diff` で確認した
（`TODO.md` と `src/README.md` は追跡済みファイルの diff、それ以外は
新規の untracked ファイル）。

前例は `git grep -cF <語> HEAD -- '*.md'` で数えた（このコミットが
入る前の状態）。

## 前例なしの語（12 語）

件数はすべて 0（前例なし）。**出てくる順ではなく、目についた順**。

- **合流**（「今日の欄への合流」「合流したときだけ真」）
  - `archives/todo/TODO-049. ....md` 129 行、
    `archives/agents/TODO-049/request-implementer-2.md` 59・69・72 行、
    `implementer-report-2.md` 29 行
  - 見立て: ToDo が「今日の欄」にも表示される（合体する）ことを指す、
    このリポジトリ固有の言い回しに見える。一般語としての「合流」は
    「流れが一つになる」意味では通じるが、UI の文脈でこの使い方が
    一般的かは判断できない

- **薄まる**（「意図が薄まる」）
  - `TODO.md` 218 行相当（TODO-056 節）、`request-implementer-2.md`
    55 行、`reviewer-report.md` 93 行、`archives/todo/TODO-049. ....md`
    126 行
  - 見立て: テストの検証意図が弱まる、という比喩。日常語の転用で、
    一般に通じる範囲だと思う

- **近道**（「この近道に入らなかった」「近道に入るようになった」）
  - `request-implementer-3.md` 55・58 行、`archives/todo/TODO-049.
    ....md` 105 行
  - 見立て: コードの早期リターン経路を指す比喩。一般語の転用で、
    通じると思う

- **無防備**（「`sessionStorage` が無防備だった」）
  - `README.md`（agents）56 行、`archives/todo/TODO-049. ....md` 118 行
  - 見立て: 一般的な日本語（ガード・例外処理が無い、の意味）。
    通じると思う

- **掃除**（「`my.js` の掃除」）
  - `archives/agents/TODO-049/README.md` 8 行（分担の表）
  - 見立て: 不要コードの削除を指す一般的な比喩。通じると思う

- **フレーク**（「曜日でフレークすることはない」）
  - `reviewer-report.md` 90 行
  - 見立て: テスト業界では "flaky test" が定着した用語（カタカナなら
    「フレーキー」「フレーク」）だが、**このリポジトリでは初出**。
    `CLAUDE.md` は「定着した用語があればそちらを使う」としており、
    英語由来のカタカナ用語として通用するかは main の判断が要る

- **導線**（「主要な導線をひととおり押さえるか」）
  - `TODO.md` 225 行（TODO-056 節）
  - 見立て: UI/UX 分野で「ユーザーの操作の流れ」を指す一般的な
    業界用語。通じると思うが、このリポジトリでは初出

- **死んだ関数**（「死んだ関数を残すより」）
  - `implementer-report.md` 135 行
  - 見立て: dead code の直訳的な言い回し。プログラミングでは
    「デッドコード」がより定着した表現で、「死んだ関数」は
    このリポジトリだけの言い換えに見える

- **境目**（「ToDo の境目のテスト」「週の境目」「`todo_days` の境目」）
  - `archives/todo/TODO-049. ....md` 126・129 行、
    `request-implementer.md` 117 行、`request-implementer-2.md`
    52・72 行、`implementer-report.md` 65 行、`implementer-report-2.md`
    64 行
  - 見立て: 「境界」の日常語的な言い換え。一般に通じると思うが、
    使用頻度が高く目についた

- **白いまま**（「画面が白いまま止まる」）
  - `README.md`（agents）57 行、`reviewer-report.md` 37 行、
    `request-implementer-2.md` 27 行、`archives/todo/TODO-049. ....md`
    121 行
  - 見立て: 白い画面のまま固まる、という一般的な言い回し（"white
    screen" の直訳的表現でもある）。通じると思う

- **無言で**（「打ち消しが無言で効かなくなる」）
  - `reviewer-report.md` 64 行
  - 見立て: 「エラーも出さず」を指す比喩的な言い回し。一般に通じる
    範囲だと思う

- **自明に**（「TITLE が無いのは自明に真になり」）
  - `reviewer-report.md` 86 行
  - 見立て: 数学・論理学由来の一般語（trivially true の訳語として
    定着）。通じると思う

## 前例が少数あった語（参考、造語の候補としては外した）

以下は 1〜3 件だけ前例があり、既に使われている語なので候補には
入れていない。念のため書いておく。

- 丸める（1 件）
- 光る（0 件だが「光らせる」「光らせ」で 6 件ヒットしており、
  活用形の違いで語としては既出と判断）
- 収まる（7 件）
- 打ち消し（13 件）

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-049. 1 画面 1 週間の表示にする.md`
- `archives/agents/TODO-049/README.md`
- `archives/agents/TODO-049/request-implementer.md`
- `archives/agents/TODO-049/request-implementer-2.md`
- `archives/agents/TODO-049/request-implementer-3.md`
- `archives/agents/TODO-049/request-reviewer.md`
- `archives/agents/TODO-049/request-verifier.md`
- `archives/agents/TODO-049/implementer-report.md`
- `archives/agents/TODO-049/implementer-report-2.md`
- `archives/agents/TODO-049/implementer-report-3.md`
- `archives/agents/TODO-049/reviewer-report.md`
- `archives/agents/TODO-049/verifier-report.md`
- `src/README.md`

## 前例なしの語数

**12 語**（合流・薄まる・近道・無防備・掃除・フレーク・導線・
死んだ関数・境目・白いまま・無言で・自明に）。
