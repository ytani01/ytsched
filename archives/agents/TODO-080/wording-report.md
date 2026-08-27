# TODO-080 wording 報告

## 対象にしたファイル

- `archives/todo/TODO-080. キャッシュがファイルの更新に追随しないのを直す.md`
- `archives/agents/TODO-080/README.md`
- `archives/agents/TODO-080/implementer-task.md`
- `archives/agents/TODO-080/implementer-report.md`
- `archives/agents/TODO-080/verifier-task.md`
- `archives/agents/TODO-080/verifier-report.md`
- `archives/agents/TODO-080/reviewer-task.md`
- `archives/agents/TODO-080/reviewer-report.md`
- `TODO.md`（`git diff TODO.md`）

**`implementer-task.md` は今回のコミットに入らない。** `git status` を見ると
未追跡ファイルの一覧に無く、`git log` で TODO-077 のコミットに既に
入っていることを確認した（TODO-080 の実装前から存在していたファイルが
そのまま使い回されている）。中身に変更は無いので、この文書に出てくる語は
すべて `HEAD` の時点で既に前例がある（自分自身が前例になる）。読みはしたが、
以下の「前例の無い語」には含めていない。

## 前例の無い語（前例の少ない順）

いずれも `git grep -cF <語> HEAD -- '*.md'` の結果。

### 1. `循環参照`（0 件）

- `archives/agents/TODO-080/implementer-report.md` 26 行目:
  「（`main_handler` 側の定数へは依存させていない。循環参照になるため）」
- 見立て: 一般的な IT 用語で、造語ではない。`.md` での初出というだけ。

### 2. `単一ブロック`（0 件）

- `archives/agents/TODO-080/reviewer-report.md` 74 行目:
  「`with open(...) as f:` の単一ブロックの末尾に置かれており」
- 見立て: 「単一」＋「ブロック」の組み合わせで、特別な呼び名という
  よりは普通の説明。造語には見えない。

### 3. `噛み合わせ`（0 件）

- `archives/agents/TODO-080/reviewer-task.md` 12 行目:
  「TODO-077 で入れた `_dirty_sdf` との噛み合わせ。」
- `archives/agents/TODO-080/reviewer-report.md` 40 行目（見出し）:
  「依頼書の項目 1（`_dirty_sdf` との噛み合わせ）は問題無し」
- 見立て: 「機能同士の絡み合い」を指す比喩として使っている。日本語として
  自然だが、このリポジトリでは初出。「相互作用」「絡み」などで言い換え
  られなくもなく、このリポジトリ独自の言い回しに見えなくもない。
  判断できない。

### 4. `見張る` / `見張り始める`（いずれも 0 件。近い語「見張り」は
  `archives/agents/TODO-020/verifier-report.md` に 1 件のみ）

- `archives/todo/TODO-080. キャッシュがファイルの更新に追随しないのを
  直す.md` 60 行目:
  「`save()` のあとで見張り始めていては遅い。見張る位置を前へ動かし」
- `archives/agents/TODO-080/README.md` 24 行目:
  「見張り始めるのが遅く」
- `archives/agents/TODO-080/implementer-report.md` 76 行目:
  「見張り始めるのが遅く」
- 見立て: `mock.patch` を仕掛けるタイミングを指して「見張る」と呼んで
  いる。TODO-020 に名詞形「見張り用」の前例が 1 件あるが、動詞「見張る」
  「見張り始める」はここが初出。一般語ではあるが、テストの用語としては
  このリポジトリ内でまだ定着していない言い回しに見える。

### 5. `切りの良い数`（0 件）

- `archives/agents/TODO-080/implementer-report.md` 47 行目:
  「`DEF_CACHE_SIZE` は 1450（計算上の最小値）ではなく 1500（切りの良い
  数への余裕）にした」
- 見立て: ごく普通の日本語表現。造語には見えない。初出というだけ。

## 参考: 前例が十分にあり、挙げなかった語の一部

`追随`（40 件）、`退行`（49 件）、`実害`（61 件）、`確信度`（108 件）、
`逸脱`（18 件）、`差し替え`（79 件）、`ダブルタップ`（12 件）、
`キャッシュミス` / `cache miss`、`分解能`（3 件）、`取りこぼし`（25 件）、
`持ち直す`（`implementer-task.md` 経由で既に 1 件。前述の理由でこの
コミットの新規語には数えていない）は、いずれも前例があるため除外した。

`is_stale` / `_stat_key` はコードの識別子（メソッド名・属性名）で、
文章の呼び名ではないため、造語チェックの対象からは外した。

## 前例の無い語数

**5 語。**（`循環参照`・`単一ブロック`・`噛み合わせ`・`見張る／見張り
始める`・`切りの良い数`）
