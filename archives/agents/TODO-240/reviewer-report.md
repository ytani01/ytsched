# TODO-240 reviewer 報告

対象: `git diff -- docs/`（UsersGuide.md の 1・3.1・8 節と目次、Install.md の 5 節）。
実装は読んだだけで、アプリは起動していない（reviewer の役割外）。

## 結論
実装との食い違いは無し。要修正なし。検討 1 件、確信度の低いもの 1 件。

## 一致したもの（1 行ずつ）
- 内容か添付があると開閉ボタンが付く: sde.html:144
- 画像はその場に表示し、押すと別のタブ: sde.html:170（`target="_blank"`）
- 画像以外はファイル名リンクでダウンロード: sde.html:173、attach_handler.py:49,57（SVG もダウンロード）
- 内容が空のとき「添付 N 件」: sde.html:165
- 閉じているあいだ添付は出ない: CSS `.my-sde-attach { display:none }`、開くと block
- 編集画面で選択欄が内容欄の下、複数選択可: edit.html:171（`multiple`）
- 付いているファイルが選択欄の上に名前で並び、別のタブで開く: edit.html:161-170
- 外すは「外す」に印を付けて保存: edit.html:164、sched_update.py:179
- 更新・完了の保存時に添付: sched_update.py:162（fix/update/add のすべて）。ボタン名は UsersGuide.md:85-88 と合う
- 同名は `名前-1.拡張子`: attach.py:147-150
- 複製で付かない: sched_update.py:119（`sde_id=None` で別の UUID）
- ゴミ箱に残るあいだは消えず、復活で見える: trash_handler.py:85-107（UUID を引き継ぐ）
- 版が予定にもゴミ箱にも無いと消える: trash_handler.py:142-158,183
- 版ごとでなく予定ごと: attach.py:7、data-format.md:177
- 上限は `--size-limit`、既定 100MB: webapp.py:46,127、__main__.py:223
- 添付の置き場 `attachments/`: attach.py:45
- 目次アンカー `#31-添付ファイル`: 既存の `#91-…` と同じ規則（ドットを除き空白をハイフン）で合う
- Install.md への参照見出し「5. リバースプロキシ」: Install.md:100 に実在
- data-format.md「添付ファイル」への相対リンク: 同じ `docs/` 内で正しい

## 検討
1. **UsersGuide.md:161-165（8 節）「版」の語が利用者向けに通じない。**
   画面に「版」は出ず、同じ文書の他の節にも無い。「その予定の版が予定にも
   ゴミ箱にも無くなったとき（編集前の版も含めて…）」は、利用者には意味が
   取りにくい。実害は読みにくさだけ。

## 確信度の低いもの
- UsersGuide.md:52「閉じているあいだ「添付 N 件」と出る」: 開いたときも
  同じ文字は残る（sde.html:165 は閉じ開きで出し分けていない）。「閉じている
  あいだ」と限る書き方が、開くと消えるようにも読める。実害は未確認。
- Install.md の追記: 「アプリの `--size-limit`」の指定先（systemd の
  ユニットなど）は 4 節に書いていない。足すかは main の判断。

## 造語・直訳調
気になる言い回しは無し。
