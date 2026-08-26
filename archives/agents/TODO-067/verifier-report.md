# TODO-067 verifier 報告

## lint / test

- `mise run lint` — ○（ruff format 26 files unchanged / ruff check 全通過 /
  basedpyright 0 errors / mypy no issues）
- `mise run test` — ○ 444 件全通過

## フッターの縦位置（幅 412px、playwright）

`uv run ytsched webapp --datadir /tmp/todo067-verify --port 10086` を起動し、
別プロセスで測定（測定後 kill 済み、`/tmp/todo067-verify` も削除済み）。

メニューを開いた状態で 11 要素の中心を測ったところ、**上段（date /
todo_days_form svg / todo_days / form_filter svg / filter_str）が
全部 740.0**、**下段（menu svg / back / forward / home / form_search svg /
search_str）が全部 777.0** で揃っていた。

main の報告は 840.0 / 877.0 で、値そのものは私の測定と違うが、これは
ビューポートの高さ（`viewport={"width": 412, "height": 800}` を使った）の
違いによるもの。**「同じ値に全部揃う」という結果は一致**している。

## フッター以外への影響（要判断）

archives の記述は「検索結果の画面（`main.html` の検索期間の行）と
編集画面（`edit.html` の `align-bottom`）は、どちらも見た目は変わって
いない」としているが、**実際に変更前・変更後を並べて撮り比べたところ、
どちらも数ピクセルのずれが生じている**。

手順: `git diff` の対象 2 ファイルだけを HEAD の内容に戻したコピー
（`/tmp/ytsched-before`、作業後に削除済み）を用意し、別ポート（10087）で
起動。同じ URL を変更前後の両方で叩いて `getBoundingClientRect()` で比較、
Pillow で画素差分も取った。

- **`main.html` の検索期間行**（`?search_str=...` でアクセス、search と
  circle-up-fill の 2 アイコンが `<br/>` で縦に並ぶ列）:
  - 変更前: search アイコン top=0 / bottom=20、circle-up-fill top=25 / bottom=45
  - 変更後: search アイコン top=2.77 / bottom=22.77、circle-up-fill
    top=26.77 / bottom=46.77
  - **2.77px 下にずれている**。画素差分でも bbox (26,2)-(42,45) に
    339 ピクセルの差（max diff 187）が出た
- **`edit.html` の `align-bottom` アイコン**（`/ytsched/edit?date=...` の
  1 行目、circle-up / dot-circle / circle-down）:
  - 変更前: top=4 / bottom=26.5
  - 変更後: top=8.5 / bottom=31
  - **4.5px 下にずれている**。画素差分でも bbox (12,6)-(98,30) に
    907 ピクセルの差
  - 目で見た限りでは、変更後のほうが同じ行の日付入力欄と縦位置が
    近くなっており、むしろ改善に見えなくもない（判断は main に委ねる）

**どちらも「見た目が変わっていない」とは言えない。** 数ピクセル程度で
気づきにくいが、実測でも画素差分でも確認できる差なので、archives の
記述（「どちらも見た目は変わっていない」）は事実と食い違っている。
この記述をどう扱うか（書き直す／許容範囲として残す）は main の判断が
要る。

## サーバーログ

例外・トレースバックなし（404 が 2 件記録されているのは、私が
`/edit?date=...` を `url_prefix` 抜きで叩いた自分のミスによるもの、
その後 `/ytsched/edit?date=...` で解決）。

## コードと archives の記述の整合性

`git diff` の内容（`.align-middle`/`.align-bottom` の移動、
`my-icon-lg` への統一、filter 列の `my-fs-medium` 化、
`.my-row-middle` の追加）は archives の「やったこと」の記述と一致していた。
