# TODO-077 wording 報告（2回目）

対象は TODO.md の diff・`archives/todo/TODO-077. ….md`・
`archives/agents/TODO-077/` 配下 7 ファイル（README・依頼書 3 つ・
報告 3 つ）。前例は `HEAD`（59c3260）を基準に `git grep -cF` で数えた。

前例が少ない順に並べる。

## 前例なし（0 件）

### 頑丈
- `reviewer-report.md:63`「設計として『`SchedDataFile` を直接覚える』方が
  頑丈だとは思うが」
- 見立て: 一般的な日本語の比喩（頑丈な設計）。造語ではなく、
  たまたま初出。問題なさそう

### 踏みやすい
- `reviewer-report.md:33`「実際に踏みやすいかは、`cmd_del()` 成功後
  `cmd_add()` が例外を出す条件次第」
- 見立て: 「経路を踏む」＝「その分岐を通る」の意味で使っている。
  一般語ではあるが、「壊れやすい／起きやすい」と書いても通じるところを
  「踏みやすい」と言い換えている。このリポジトリでの言い回しかは
  判断できない

### 覚えさせる
- `implementer-task.md:19`「変更のあった日付を `SchedData` 側に
  覚えさせる」
- 見立て: 「保持させる」の平易な言い換え。普通の日本語で、
  問題なさそう

### 素直な入力
- `reviewer-report.md:34`「`SchedDataEnt` の直接コンストラクタは
  素直な入力では例外を出しにくく」
- 見立て: 「単純な／扱いやすい入力」の意味。一般的な比喩の範囲内に見える

### 溜まった
- `reviewer-report.md:17`（コード注釈内）「溜まった `_dirty_dates` を
  まとめて保存し」
- 見立て: 普通の日本語（積み上がった、の意味）。問題なさそうだが
  「溜める」を状態管理の用語として使っているので念のため挙げる

### 乗っていない
- `reviewer-report.md:51`「メモリ上で行った変更（…の結果）が
  乗っていないので、変更はディスクへ一度も書かれずに消える」
- 見立て: 「変更が反映されていない」の意味を「乗る」で表す比喩。
  一般にも使われる言い方だが、このリポジトリでの初出。問題は
  無さそうに見える

## 前例が少ない（1 件）

### 紛れ込む
- `archives/todo/TODO-077….md:54`「次の関係の無いリクエストの保存に
  紛れ込む」、`README.md:27`、`reviewer-report.md:29`
- 前例 1 件（別文書）
- 見立て: 一般的な日本語。問題なさそう

### 引き直し（「引き直す」の名詞形）
- `archives/todo/TODO-077….md:49`「日付から引き直したときに」、
  `reviewer-task.md:13`「`get_sdf()` で引き直している点」
- 「引き直す」自体は前例 5 件あるが、名詞形「引き直し」は 1 件
- 見立て: 動詞「引き直す」（キャッシュから再取得する、の意味）の
  活用違いで、問題なさそう

### 悪化
- `implementer-task.md:41`「悪化ではない」、`reviewer-report.md:28,36`
- 前例 1 件
- 見立て: 一般的な日本語。問題なさそう

### 追い出（される）
- `reviewer-report.md:49,50`「キャッシュから…追い出されていると」
- 前例 1 件
- 見立て: LRU キャッシュの比喩として一般的。問題なさそう

### 戻し忘れ
- `verifier-task.md:21`「戻し忘れないこと」、`verifier-report.md:33`
- 前例 1 件
- 見立て: 普通の日本語。問題なさそう

## 参考（前例は複数あるが、内容上ここで初めて使われた言い回し）

### 中間状態
- タイトル「`fix` で `.bak` が中間状態に上書きされる」、
  `reviewer-task.md:3`、`verifier-task.md:3`
- 前例 8 件（別の意味・別文脈のものを含む）
- 見立て: この項目の核心を表す語で、一般的な IT 用語（中間状態）の
  範囲内に見える

### 無条件
- `implementer-report.md:40`、`verifier-report.md:89`、
  `reviewer-report.md:24,71`
- 前例 5 件
- 見立て: 一般的な日本語。問題なさそう

## 読んだファイル

- `archives/todo/TODO-077. fix で .bak が中間状態に上書きされるのを直す.md`
- `archives/agents/TODO-077/README.md`
- `archives/agents/TODO-077/implementer-task.md`
- `archives/agents/TODO-077/verifier-task.md`
- `archives/agents/TODO-077/reviewer-task.md`
- `archives/agents/TODO-077/implementer-report.md`
- `archives/agents/TODO-077/verifier-report.md`
- `archives/agents/TODO-077/reviewer-report.md`
- `TODO.md`（`git diff` で差分のみ）

## 前例の無い語数

6 語（頑丈・踏みやすい・覚えさせる・素直な入力・溜まった・乗っていない）。
1〜3 件の語（紛れ込む・引き直し・悪化・追い出・戻し忘れ）を含めても
普通の日本語の範囲に見え、「足場」のような造語は見当たらなかった。
