# TODO-141 implementer 依頼

## 目的

ゴミ箱に表示されている項目をチェックボックスで複数選択し、ヘッダーの
ゴミ箱アイコンからまとめて完全に削除できるようにする。

## 対象範囲

`TODO.md` の TODO-141 だけを実装する。主な対象は次のファイル。

- `src/ytsched/trash.py`
- `src/ytsched/trash_handler.py`
- `src/ytsched/webroot/templates/trash.html`
- `src/ytsched/webroot/static/js/trash-page.js`
- `src/ytsched/webroot/static/css/my.css`
- `tests/test_trash.py`
- `tests/test_web.py`
- `tests/test_browser.py`
- `docs/User.md`
- 必要なら `src/README.md` / `tests/README.md`

`TODO.md` は main が扱うので編集しない。実データ `~/ytsched/data` は
使わない。`mise run upgradeproject` は実行しない。コミットしない。

## 決まっている仕様

### 画面

- 各項目の個別削除アイコンをチェックボックスへ置き換える。復活ボタンは
  残す
- ヘッダーに「表示中をすべて選択」するチェックボックスを置く
- ヘッダー右端のゴミ箱アイコンは、選択した項目をまとめて削除する
  ボタンにする。未選択時は `disabled`
- 一部だけ選んだとき、全選択チェックボックスは `indeterminate` にする
- 確認文は「選択した N 件を完全に消します。よろしいですか?」のように、
  選択件数を含める
- 「すべて選択」は `TrashMax` により**現在 HTML に表示されている項目
  だけ**を選ぶ。未表示の古い項目は選ばず、削除しない
- 既存の `data-confirm` / `trash-page.js` による確認を使い、インライン
  イベントハンドラは使わない
- チェックボックスとボタンには内容の分かる label / `aria-label` を付ける
- スマホ幅でヘッダーと各行が崩れないようにする

ヘッダーの一括削除 form と、本文にあるチェックボックスは、HTML の
`form` 属性で関連付けると、復活用 form と入れ子にせずに済む。送信値の
具体的な作り方は任せるが、サーバーが `sde_id` と `trashed_at` の組を
確実に復元できること。JavaScript が動かなかった場合も、誤った組を
削除せず 400 にすること。

### HTTP

- 選択削除用の `cmd` を追加し、`sde_id` と `trashed_at` の組を複数受ける
- 0 件、組の数が合わない、値の形式が不正な POST は 400 にし、
  `trash.jsonl` を書き換えない
- 送られた組が 1 件も存在しなければ 404 にし、書き換えない
- 存在する選択項目だけを削除する。選択していない項目は残す
- 削除後、表示できる項目が 1 件でも残れば `/ytsched/trash`、0 件なら
  `/ytsched/` へ redirect する。表示外の古い項目があれば「残る」側
- `sde_id` 絞り込み画面からの選択削除も、対象は表示中だけ。削除後の
  redirect は絞り込みを外した `/ytsched/trash` でよい
- UI から使わなくなる個別削除・全消去の HTTP 分岐は、参照が無ければ
  整理する。`TrashFile.delete()` は `delete_many()` の薄いラッパとして
  残してもよい

### データ処理

- `TrashFile` に複数の `(sde_id, trashed_at)` を一度に削除する処理を足す
- `trash.jsonl` は一度だけ書き直す
- 同じ組の行が複数あればすべて削除し、実際に削除した行数を返す
- 選択していない正常な行、JSON として読めない行、JSON object でない行は
  バイト内容を変えずに残す
- 1 件も一致しない場合はファイルを書き直さない
- 既存ファイルのパーミッションを維持する
- 全消去専用の `clear()` が不要になれば削除し、説明とテストも追随させる

## テスト

少なくとも次を自動テストへ入れる。

- データ層: 複数削除、未選択・壊れた行・表示外相当の行が残る、重複した組、
  一致なし、空選択、パーミッション維持
- HTTP: 複数削除、一部を残すとゴミ箱へ redirect、全部消すと週間表示へ
  redirect、表示上限より古い行が残る場合、0 件・不正な組・全件不明
- HTML: 項目チェックボックス、全選択、未選択時 disabled、個別削除 form と
  `cmd=clear` が無いこと
- JavaScript / ブラウザ: 個別選択、全選択、一部選択時の indeterminate、
  選択件数入り確認、キャンセルでは変化なし、承認で選択項目だけ削除、
  未表示項目が残る

最後に relevant test、formatter、lint、型チェックをまとめて実行し、可能なら
一時データで実動作も確認する。

## 完了条件

- TODO-141 のチェック項目をすべて満たす
- 既存の復活操作と壊れた行の保護を壊さない
- テスト・formatter・lint・型チェックが通る
- `archives/agents/TODO-141/implementer-report.md` に変更、確認結果、判断、
  残る懸念を簡潔に書く
