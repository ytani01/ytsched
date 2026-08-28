# TODO-090 wording 報告

対象は下記「読んだファイル」の全 `.md`。`git diff --cached` は空だったので、
`git status`（`-uall` は使わず）で作業ツリーの変更・untracked を確認し、
TODO-090 のコミットに入る想定のファイルを拾った。前例の判定は
`git grep -cF <語> HEAD -- '*.md'`（`|| true` 付き）で行った。

候補は前例の件数が少ない順。

## 前例の無い語（0 件）

- **`共有インスタンス化`**
  出てくる場所: `reviewer-report.md:59`「`conf.json` については、
  **共有インスタンス化**によって新しく生まれた問題だと考える」
  前例: 0 件
  見立て: 「1 インスタンスを複数箇所で共有する形にする」という意味の
  名詞化。一般語ではなく、このリポジトリでの言い回しに見える。
  「共有する形にしたこと」のような普通の言い方で足りそうだが、
  判断は main に委ねる。

- **`_dirty を下ろす` / `_dirty が下りる`**
  出てくる場所: `implementer-report.md:89, 99`、`verifier-report.md:96`、
  `archives/todo/TODO-090. ….md:71`「警告を 1 行出して `_dirty` を
  **下ろす**」
  前例: 0 件（`下ろす`／`下りる`／`が下りた` いずれも HEAD の `.md` に
  無い。TODO-048 の「描き下ろす」は別の意味での一致）
  見立て: フラグ（真偽値）を倒す操作を「下ろす／下りる」と呼ぶのは、
  一般に通用する比喩ではあるが、この語自体は初出。実装ファイル内の
  コメント・docstring でどう書かれているかは確認していない
  （`.md` の中だけを見ている）。

- **`ConfFile` / `AppInfo` / `ConfArgs`**（クラス名。`ConfArgs` は
  `TestConfArgs` を除いて検索）
  出てくる場所: `src/README.md` のクラス図・本文、
  `archives/agents/TODO-090/README.md`・`implementer-report.md` など
  前例: いずれも 0 件
  見立て: これは文章上の言い回しではなく、`README.md`（着手前に main が
  決めたこと）で決めた**設計上の新しいクラス名**。TODO-021 の「足場」の
  ような、書いた本人が気づかない比喩的な造語とは性質が違うと考えるが、
  判断は main に委ねる。

- **`frozen dataclass`**
  出てくる場所: `src/README.md`・`archives/agents/TODO-090/README.md`・
  `implementer-report.md` の複数箇所
  前例: 0 件
  見立て: Python の一般的な用語（`dataclasses.dataclass(frozen=True)`）
  で、このリポジトリでは初出なだけ。造語ではなさそう。

## 前例が少ない語（1 件）

- **`変更の検出`**
  出てくる場所: `TODO.md`（旧 TODO-090 節、目次へ移動する前の本文）
  「`conf.json` も、キャッシュ + **変更の検出**で読み」
  前例: 1 件（`TODO.md` 自身の同じ行。今回のコミットは節を削除して
  archives へ移すだけなので、実質は同じ文の位置が変わっただけ）
  見立て: 一般的な言い方で、問題ないと考える。

## 判断できないもの

- **`低確信度の指摘`**
  出てくる場所: `implementer-report.md:94`「reviewer の**低確信度の
  指摘**（`is_stale()` の重複）は指示どおり直していない」
  前例: `低確信度` 自体は 0 件だが、`確信度: 低` という見出しの形
  （`.claude/agents/reviewer.md` 由来）は TODO-028 に 1 件ある。
  同じ概念を名詞句にしただけとも読めるが、一般に通用する言い方かは
  判断できない。

## 前例があり、問題無さそうなもの（参考）

念のため拾ったが、件数が多く定着している語なので候補には数えていない。
`委譲`（35 件）、`副作用`（26 件）、`持ち直す`（7 件）、`使い回す`（2 件）、
`巻き込まれ`（3 件）、`往復`（31 件）、`確信度`（127 件）。

## 読んだファイル

- `TODO.md`（差分。TODO-090 節の削除と目次への 1 行追加のみ）
- `archives/todo/TODO-090. 依存の渡し方と、キャッシュ・conf.json の扱いを揃える.md`
- `archives/agents/TODO-090/README.md`
- `archives/agents/TODO-090/implementer-report.md`
- `archives/agents/TODO-090/verifier-report.md`
- `archives/agents/TODO-090/reviewer-report.md`
- `src/README.md`（差分）

## 前例の無い語の数

0 件の候補は 6 語（`共有インスタンス化`、`_dirty を下ろす/下りる`、
`ConfFile`、`AppInfo`、`ConfArgs`、`frozen dataclass`）。判断できないもの
1 語（`低確信度の指摘`）を含めると 7 語。TODO-025 の目安（造語混入時
15 語、通常 1〜3 語）と比べると中間的だが、後半 4 語（クラス名・
Python 用語）は文章の言い回しというより設計上の命名・専門用語なので、
実質の候補は `共有インスタンス化`・`_dirty を下ろす`・`低確信度の指摘`
の 2〜3 語程度と見ている。
