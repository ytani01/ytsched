# TODO-057 wording 報告（2 回目・完了コミット分）

対象は「決着後のコミットに入る `.md`」全部。決めごとのコミットで確認済みの
5 語（「振り切り」→「速く払ったとき」に直したもの、「パネル」「絶対配置」
「通常フロー」「送る判定」）はここでは挙げ直さない。

前例の件数が少ない順（同数は並記）。

## 巻き戻り／巻き戻って／巻き戻す

- **出てくる箇所**: `request-implementer-2.md:26,72`「送り終えた直後に、
  元の週へ巻き戻って見える」、`implementer-report-2.md:16,49`、
  `reviewer-report.md:51`「ラッパーの中央への巻き戻しが 2 回起きる」、
  `request-verifier.md:101`、`verifier-report.md:71,77,90`、
  `archives/todo/TODO-057. …md:121,148`
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般語としては通用する（「巻き戻す」自体は普通の日本語）。
  ただしこのリポジトリでは初出で、reviewer・verifier・implementer の
  3 者が同じ意味で揃って使っているので、指す現象は共有できている。
  問題があるとすれば「造語」というより、**この文書群だけで急に頻出した
  語**という点

## 連打

- **出てくる箇所**: `reviewer-report.md:37`「◀▶ を連打する」、
  `request-implementer-2.md:14,71`、`request-verifier.md:97`、
  `implementer-report-2.md:49`、`verifier-report.md:60,64`、
  `archives/todo/TODO-057. …md:117,144`
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般に通用する普通の日本語（「ボタンを連打する」）。
  リポジトリでの初出というだけで、造語には見えない

## 縦のずれ

- **出てくる箇所**: `request-implementer.md:92,156`「縦のずれを別に
  補正する必要は無いはず」、`implementer-report.md:56`、
  `archives/todo/TODO-057. …md:91`
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 「縦」＋「ずれ」の組み合わせで、意味は素直に取れる。
  一般語の組み合わせであって造語ではなさそう

## 相乗りして（発火する）

- **出てくる箇所**: `reviewer-report.md:53`「A の `finish()` はまだ
  `done=false` なので実行され…B の `transitionend` に相乗りして発火する」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 「1 つのイベントに複数のリスナーが便乗して呼ばれる」ことの
  比喩。一般語としても通じるが、やや口語的な言い換え。他の担当が同じ現象を
  別の言い方（「両方が呼ばれる」）で説明している箇所もあるので、
  **このリポジトリだけの言い換えに近い**かもしれない。判断は付けにくい

## 垂直方向優位

- **出てくる箇所**: `implementer-report.md:57`「垂直方向優位のドラッグ
  （dx=10, dy=-100）では `transform` が付かず」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 「縦方向の動きが横方向より大きい」ことを指す。意味は
  文脈から取れるが、リポジトリの他の箇所（`SWIPE_X_PER_Y` など）は
  「縦との切り分け」のように普通の言い方をしている。**やや硬い言い換え**
  に見える

## 中身の無い余白

- **出てくる箇所**: `request-implementer-2.md:47`「動いた分が中身の無い
  余白として見える」、`reviewer-report.md:73`
- **`git grep -cF` の件数**: 0 件（前例なし。「余白」単独では 41 件の前例
  あり）
- **見立て**: 「余白」に「中身の無い」を添えただけで、一般の日本語の
  範囲内。造語ではなさそう

## 偶発的

- **出てくる箇所**: `verifier-report.md:25`「ブリンクカーソルのタイミング
  による偶発的なピクセル差」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般的な日本語の専門語（「偶発的」）。造語ではない

## 実行コンテキスト

- **出てくる箇所**: `verifier-report.md:76`、
  `archives/todo/TODO-057. …md:150`
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: ブラウザ・JavaScript の一般的な専門用語（execution
  context の訳語）。リポジトリでの初出というだけ

## 描画タイミング

- **出てくる箇所**: `reviewer-report.md:95`「ブラウザの描画タイミング
  次第で確実に起きるとは言い切れず」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般的な言い回し。造語ではなさそう

## オーバーレイ

- **出てくる箇所**: `reviewer-report.md:91`「画面全体を覆う不透明な
  オーバーレイではない」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般的な IT 用語（カタカナのまま使う語）。問題なさそう

## 同期処理

- **出てくる箇所**: `reviewer-report.md:92`「`transform=""` から
  `location.href` の代入までは同期処理だが」
- **`git grep -cF` の件数**: 0 件（前例なし）
- **見立て**: 一般的な IT 用語。造語ではない

## 判断できないもの

- **打ち切る形**（`request-implementer-2.md:17`「前の呼び出しを打ち切る形
  にする」）— 「打ち切る」単独は 5 件の前例があるが、いずれも「検索を
  一定件数・日数で打ち切る」の意味。今回は「後発の呼び出しが先発の
  呼び出しを中断させる」という別の使い方で、**語としては前例があるが
  意味の広げ方はここが初出**。前例の有無だけでは切れないので判断できない

## 読んだファイル

- `TODO.md`
- `archives/todo/TODO-057. スワイプで隣の週を指に追従させる.md`
- `archives/agents/TODO-057/README.md`
- `archives/agents/TODO-057/request-implementer.md`
- `archives/agents/TODO-057/request-implementer-2.md`
- `archives/agents/TODO-057/request-reviewer.md`
- `archives/agents/TODO-057/request-verifier.md`
- `archives/agents/TODO-057/implementer-report.md`
- `archives/agents/TODO-057/implementer-report-2.md`
- `archives/agents/TODO-057/reviewer-report.md`
- `archives/agents/TODO-057/verifier-report.md`

## 前例なしの語数

11 語（「打ち切る形」は判断できないものとして別扱い、含めれば 12 語）。
