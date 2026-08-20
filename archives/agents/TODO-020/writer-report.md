# writer の報告（TODO-020）

TODO-020（JSON Lines への移行）の実装に合わせて、`CLAUDE.md` と
`docs/data-format.md` を書き直した。コードは変えていない。

## 読んだもの

- `TODO.md` の TODO-020
- `archives/agents/TODO-020/implementer-request.md`
- `archives/agents/TODO-020/implementer-report.md`（末尾の
  「reviewer の指摘への対応」まで含む）
- `archives/agents/TODO-020/reviewer-report.md`、`verifier-report.md`
- 実装本体: `src/ytsched/ytsched.py`（`normalize()` /
  `SchedDataEnt.to_dict()` / `from_dict()` / `SchedDataFile.load()` /
  `load_line()` / `save()` / `skipped_lines`）、`src/ytsched/migrate.py`
  （`decode_line()` / `split_fields()` / `conv_date()` / `conv_time()` /
  `html2text()` / `Migrator`）、`src/ytsched/__main__.py` の `migrate`
  サブコマンド定義
- `uv run ytsched migrate --help` を実行し、オプション名・既定値・
  ヘルプ文を文書の記述と突き合わせた

## 変更したファイル

### `CLAUDE.md`

- 冒頭「これは何か」の「まだ実装していないので…旧形式のまま」を、
  実装済みの書き方に直した
- 「データモデルの勘所」を新形式に合わせて書き直した。
  - `SchedDataEnt` の `detail` の説明から `htmlstr2text()` /
    `text2htmlstr()` を外し、「常に素のテキスト・変換しない」に。
    `normalize()`（判定・検索の照合にだけ使い、保存する文字列は
    変えない）を新しい箇条書きとして追加
  - `SchedDataFile` のパスを `.jsonl` に、文字コードを utf-8 のみに、
    読み込みを「行ごとにデコード・パース」に書き直した
  - **飛ばした行を次の `save()` で末尾へ元のバイトのまま書き戻す**
    振る舞いを新しい箇条書きとして追加（implementer 報告の
    「reviewer の指摘への対応 1」を要約）
  - `.bak` の仕組み自体は変えていないので、その説明は維持した
- 「コマンド」に `ytsched migrate` の実行例を足した
  （`uv run ytsched migrate --datadir ~/ytsched/data`）

### `docs/data-format.md`

- 冒頭の「状態」を「まだ実装していない」から「実装済み」に直した
- 「壊れた行の扱い」に、書き戻しの振る舞いを 1 段落足した
  （implementer 報告の 4 行を下敷きに、この文書の文体に合わせて
  書き直した）
- 同じ節の「飛ばす行」一覧に、抜けていた
  「utf-8 でデコードできない行」を足した（実装
  （`load_line()` の `UnicodeDecodeError` 処理）にはあるのに文書の
  一覧に無かった食い違い）
- 「旧形式（タブ区切り）からの移行」に「移行ツールの使い方」を
  新設し、`ytsched migrate` のオプション（`--datadir` /
  `--dry-run` / `--error-file` / `--debug`）、既に `.jsonl` がある
  ファイルは飛ばすこと、元の `.cgi` は消さないこと、変換できない
  行は `--error-file` へ書き出すことを書いた。「変換の手順」1〜6の
  中身は変えていない

## 書けなかったところ・確かめられなかったところ

- 「移行ツールを作るときに要るもの」節の見出しは、ツールが既に
  存在する現状だと過去形寄りの内容になっているが、内容自体
  （TODO-019 の合成テストデータの説明）は現行と食い違わないため
  そのままにした。見出しを直すかどうかは好みの範囲と判断した
- それ以外に、実装と文書の食い違いは見当たらなかった

## 空行とキャッシュの件（2026-08-21）

reviewer の指摘 A・B（`archives/agents/TODO-020/reviewer-report.md` の
「直した差分のレビュー」）に合わせて 2 点直した。コードは変えていない。

### 読んだもの

- `archives/agents/TODO-020/reviewer-report.md` の
  「直した差分のレビュー（2026-08-21）」
- `archives/agents/TODO-020/implementer-report.md` の
  「空行の書き戻しをやめた（2026-08-21）」
- `src/ytsched/ytsched.py` の `load()` / `save()` /
  `is_empty_line()`、`src/ytsched/webapp.py`、`SchedData`
  （`DEF_CACHE_SIZE = 20000`、`WebServer.__init__()` で 1 つだけ
  作られること）を実際に読んで確認した

### 変更したファイル

- `docs/data-format.md`
  - 「飛ばす行」の一覧の「空行」を「空行（空白だけの行を含む）」に
  - 「壊れた行の扱い」の書き戻しの段落を、書き戻すのは空行を除く
    4 種類だけと直し、「空行だけは書き戻さない」段落を新設
  - 「手で直せば、そこで消える」の文言を外し、代わりに
    「サーバを止めてから直すか、直したあとに再起動すること」と、
    `SchedData` のキャッシュが理由であることを 1 段落足した
- `CLAUDE.md`
  - 「データモデルの勘所」の書き戻しの箇条書きを、空行を除く
    4 種類だけと直した。詳細は二重に書かず
    `docs/data-format.md` を参照する形にした
  - サーバ再起動の注意は、`CLAUDE.md` 側の元の文言に
    「手で直せば消える」という誤解を招く表現が無かったため、
    こちらには足していない（`docs/data-format.md` にのみ書いた）

### 書けなかったところ

- 特になし
