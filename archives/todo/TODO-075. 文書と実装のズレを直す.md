# TODO-075. 文書と実装のズレを直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | verifier + wording |
| 実施 | Opus 5 / effort high | verifier + wording |
| 消費 | output 7,831 / cache_creation 112,488 / 概算 $1.8 |
|      | main 79% + wording 13% + verifier 8%（料金の割合） |

## きっかけ

文書を通して読み、実装と突き合わせてほしいという依頼から。
`README.md` / `src/README.md` / `docs/Developer.md` /
`docs/data-format.md` / `tests/README.md` の 5 本を読み、記述を 1 つずつ
コードと実物に当てて確かめたところ、8 件が実装に追いついていなかった。

どれも TODO-048 以降の変更（週表示・ゲージ・アイコン・データ形式）で
置き去りになったもので、直す先ははっきりしている。

## やったこと

### `README.md`

- **アイコンの数を 23 個から 22 個に。** TODO-070 でプラスのアイコンを
  廃止したときに減っていた
- **特徴の「無限にスクロール」を「1 画面に 1 週間。左右のスワイプで週を
  送る」に。** TODO-049 で 1 画面 1 週間になり、TODO-054 でスワイプ、
  TODO-069 で DOM の差し替えになった。無限スクロールの仕組みはもう無い
- **ゲージを「画面の端」から「画面の上部に横向き」に。** TODO-058 で
  ヘッダへ移した。TODO-074 のタップでその週へ飛べる件も足した
- **データ形式を「テキスト形式(独自)」から「テキスト形式(JSON Lines)」に。**
  あわせて「10年以上前に、Perl CGIで作成したデータをそのまま使える」を
  「`ytsched migrate` で変換して使える」に直した（TODO-018・TODO-020）

### `src/README.md`

- **`LoadMonths` の範囲を 0〜6 から 0〜24 に。** 実装は
  `MainHandler.LOAD_MONTHS_MAX = 24`
- **`webroot/static/` の説明に、アイコンと `manifest.json` を足した**
  （TODO-039・TODO-048）

### `docs/Developer.md`

- **個別コマンドの対象を `src tests` から `src tests tools` に。**
  `mise.toml` の `fmt` / `typecheck` は `tools` も見ている

### `docs/data-format.md`

- **「現在 `~/ytsched/data` は空になっている」を落とした。** 移行が
  済んで実データが入っている。合成テストデータを使う理由は「実データは
  個人の予定そのものでリポジトリに入れられない」ことなので、そちらに
  書き換えた

## テスト

文書だけの変更で、コードは 1 行も触っていない。

verifier に 8 件を 1 つずつ実物と突き合わせさせ、あわせて修正漏れが
無いかも見させた。報告は
[archives/agents/TODO-075/verifier-report.md](../agents/TODO-075/verifier-report.md)、
分担の理由は
[archives/agents/TODO-075/README.md](../agents/TODO-075/README.md)。
