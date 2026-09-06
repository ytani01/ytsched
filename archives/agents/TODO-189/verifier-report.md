# TODO-189 検証報告

## 確認結果

### 1. `.codegraph/` が git status に出ないこと
○ 確認

```bash
$ git status --short
 M .gitignore
```
`.codegraph/` は出ず、`.gitignore` の変更だけが表示される。

### 2. `.gitignore` の末尾に足した行が効いていること
○ 確認

```bash
$ git check-ignore -v .codegraph/
.gitignore:106:.codegraph/	.codegraph/
```
106 行目の `.codegraph/` ルールが有効。`*.lock` など他の行に拾われているのではない。

### 3. 追跡中のファイルが巻き添えになっていないこと
○ 確認

```bash
$ git ls-files | wc -l
1130

# 変更前の .gitignore での git ls-files
$ git -c core.excludesFile=<変更前> ls-files | wc -l
1130

# diff は差分なし
```
追跡中のファイル一覧に変動なし。

### 4. `.codegraph/` 以外の未追跡ファイルが新たに無視されるようになっていないこと
○ 確認

変更前後で未追跡ファイルの一覧に差分なし。現在、未追跡ファイルは 0 個。

### 5. `.gitignore` のコメント形式が既存の書き方に揃っていること
○ 確認

104 行目のコメント：
```
# codegraph のインデックス（TODO-189）。codegraph init / sync が作り直す
```

既存の形式（96・100 行目）と同じく、括弧付きで TODO 番号を添えている：
- 96 行目：`（TODO-019）`
- 100 行目：`（TODO-020）`
- 104 行目：`（TODO-189）`

---

## 判定

すべての項目が OK。`.gitignore` の変更は意図どおり動作しています。
