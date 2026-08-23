# TODO-038 verifier 報告

依頼書: `archives/agents/TODO-038/verifier-request.md`

前のセッションで中断していたため、最初からやり直した。比べる相手は
main の訂正どおり **コミット `cca8269`**（`git archive cca8269
src/ytsched/webroot`）で固定した（一度 `HEAD`＝`74a480a` で取り出して
しまったが、`pagetop.css`/`my_cookie.js` の削除が旧版側に混ざっている
ことに自分で気づき、取り直した）。

## 結論

**画素単位の比較で見つかった差は、あらかじめ了承されている 1 件と、
テスト手順そのものに起因するもの（後述）だけ。テンプレート・CSS の
挙動としての新しい差は見つからなかった。** 3 段目の「確認が取れていない」
2 点（`edit.html` の `@` と `my-fs-large` の `col`→`row`）は、どちらも
**画素単位で完全に一致（AE=0）** した。

## 環境

- 旧版: ポート 10097、`-r` に `git archive cca8269` で取り出した
  `webroot` を指定
- 新版: ポート 10098、作業ツリーそのまま
- どちらも `--datadir` は一時ディレクトリ
  (`/tmp/claude-649/.../scratchpad/todo038/data_old` /
  `data_new`)。`~/ytsched/data` もポート 12345 も触っていない
- 一時ファイルは
  `/tmp/claude-649/-home-ytani-work-ytsched/1aabf7d9-2054-4095-8cae-087382f1b160/scratchpad/todo038/`
  の下（`gen_data.py`／`served/`／`shots/`）
- テストデータ: 2026-08-24（今日、月曜）を中心に金〜木の 7 日分。
  普通の予定・★重要・取り消し（`x` と `(欠`、どちらも複数行の詳細付き）・
  祝日・場所あり・複数行詳細・ToDo（期限が過去/1 週間以内/先）を全部
  入れた。作業終了後は削除していない（scratchpad のまま）
- サーバ・`python3 -m http.server`（スクリーンショット用の静的配信）は
  作業終了後にすべて `pgrep` で確認して kill 済み。ポート 12345 は
  無傷（`pgrep -fa "ytsched webapp"` で確認）

## 1. 画素単位の比較

一覧・検索・編集（普通/取り消し/重要）を 412 幅・740 幅で、
`chromium --headless --screenshot` ＋ `compare -metric AE` で比較した。
詳細を全部開いた状態・メニューを開いた状態も、`.longtext-sw`/`#menu-sw`
の `checked` を JS で立てた静的 HTML を作って撮った（2 段目の
implementer と同じやり方）。

| 画面 | 幅 | AE |
|---|---|---|
| 編集（普通） | 412/740 | **0** |
| 編集（取り消し） | 412/740 | **0** |
| 編集（重要） | 412/740 | **0** |
| 一覧 | 412 | 137,773 |
| 一覧 | 740 | 277,075 |
| 検索 | 412 | 46,133 |
| 検索 | 740 | 80,155 |

編集画面は完全一致。3 段目で main が「確認が取れていない」としていた
2 点は、これで両方とも画素単位で裏が取れた。

- `edit.html` の場所の行の `<span class="my-fs-large">@</span>` → `@`
  （`<span>` ごと外した）: **差なし**
- `edit.html` の種別の行で `my-fs-large` が `col` から `row`
  （`.my-edit-row`）へ移った: **差なし**

## 一覧・検索の AE が大きいことについて（見た目としては差なし）

見た目は同じだが、AE が 0 にならない。切り分けると 2 つの原因に
分解できた。**どちらも実装の問題ではない。**

### (a) 依頼書に書いてある既知の差（了承済み）

取り消し済みの予定の詳細を開くと、上下の空行が 2 行ずつ減る
（122px→62px）。テストデータには取り消し済み・詳細ありの予定を
**2 件**入れており、詳細を全部開いた状態で撮っているので、この分だけ
本文全体が上へずれ、それより下の行がすべて「別の場所」と比較される
形になって AE が跳ね上がる。実際に画像を目で見比べても、この 2 件の
詳細欄の高さが縮んでいる以外は一致している。

### (b) chromium のレンダリングそのものの揺らぎ（テスト環境のノイズ）

取り消し済みの予定の詳細を**空にした**データで作り直し、同じ HTML を
**同じ chromium で 2 回**スクリーンショットして比べたところ、
**AE=11,812**（旧×新の比較の AE=11,813 とほぼ同じ）。同じ HTML・同じ
chromium・同じマシンでも、実行のたびに数千〜1 万強の画素が変わる。
`--fuzz 5%` を付けると AE=0 になるので、色の値が 1〜数段階ずれる程度の
アンチエイリアス/ラスタライズの非決定性で、内容の違いではない。

このマシンは他セッションの chromium が同時に何十プロセスも動いていて
（`pgrep -c chromium` で 30〜40 台）、システムが重い状態でのレンダリング
だったことも影響していると思われる。**この揺らぎは旧版・新版どちらの
スクリーンショットにも同じだけ乗るので、比較の結論（見た目は変わって
いない）には影響しない。**

### 検証の手順で見つけた、比較の落とし穴（実装の不具合ではない）

`search_str` は URL 引数で渡すと `conf.json` へ永続化され、次回以降の
既定値になる（`main_handler.py get_conf_arg()`、意図した仕様）。
最初の比較で、検索のスクリーンショットを撮る前に一覧を撮っていたのに
AE が大きく出たのは、**別の確認作業（起動確認の curl）で先に
`search_str=予定` を投げてしまい、`conf.json` に検索文字列が残った
まま一覧を撮っていたため**だった。旧版・新版で「いつ検索を投げたか」
の順序がずれていたので、日付レンジ（`date_from`/`date_to`）が
サーバごとに違う状態で一覧を撮ってしまっていた。`conf.json` を消して
サーバを再起動し、一覧の取得は必ず `?search_str=`（空）を明示して
撮り直した。**verifier 側の手順の問題であり、TODO-038 の実装には
関係ない。**

## 2. lint・test

- `mise run lint` — ruff format `23 files left unchanged`、
  ruff check `All checks passed!`、
  basedpyright `0 errors, 0 warnings, 0 notes`、
  mypy `Success: no issues found in 20 source files`
- `uv run pytest -q` — **412 passed**

## 3. 起動確認

新版（作業ツリー、`--datadir` は一時ディレクトリ、ポート 10098）で確認。

- `GET /ytsched/` → 200
- `GET /ytsched/edit/` → 200
- `GET /ytsched/edit/?date=2026-08-24&sde_id=<id>` → 200
- `GET /ytsched/?search_str=予定`（URL エンコード）→ 200
- サーバのログ（標準出力・標準エラー）に `Traceback`/`Exception` は無し

## 4. ブラウザの JavaScript 例外

`chromium --headless --dump-dom --enable-logging=stderr` で、一覧・編集を
412×915 / 740×360 の 4 通り確認。`Uncaught` / `TypeError` /
`ReferenceError` は **0 件**（出たのは chromium 自身の
`sandbox`/`idle`/`gcm` 系の無害な警告のみ）。

## 見つけたこと

**実装側の不具合は見つからなかった。**

## 判断が要る点

無し。
