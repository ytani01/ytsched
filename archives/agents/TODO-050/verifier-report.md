# TODO-050 確認の報告（verifier）

## 通ったもの

- `mise run test` → 425 passed
- `mise run lint`（ruff format / ruff check）→ 通過
- `mise run typecheck`（basedpyright / mypy）→ エラーなし
- アプリの起動（`--datadir` を一時ディレクトリにして port 18085）→
  `GET /ytsched/` が 200、サーバのログに例外なし
- **ブックマーク。** `?date=2021-03-01` を直接開くと、その日の要素
  （`#date-2021-03-01`）が出る
- **URL が変わること。** キーボードの ←/→ で `?date=...` が変わる
- **キーボードの割り当て。**
  - `/` で検索欄（`#search_str`）にフォーカスが移る
  - 検索欄にフォーカスがある状態で `abc` を打つと欄に入力される
    （画面へは反映されない＝キーが奪われていない）
  - 検索欄にフォーカスがある状態で ← を押しても URL が変わらない
    （`isTyping()` が効いている）
  - `Esc` で検索欄からフォーカスが外れる
  - `Home` で今日の日付へ移動する
- **追加・修正のあとのリロードで再送信にならないこと。**
  一覧から追加 → 保存 → 一覧へリダイレクト → リロード x2 で、
  データファイル（`2026/07/11.jsonl`）は 1 行のまま増えなかった。
  同じ行を編集画面から開いて「済」（fix）→ 一覧へリダイレクト →
  リロード x2 でも、行数は 1 のまま
- 見た目（`tools/screenshot.py` で撮った一覧・編集画面のキャプチャ）に
  崩れは無い。詳細欄が閉じた状態で 2 行になる症状（TODO-045・047）は
  再現しなかった

## 見つけたこと（いちばん大きいもの）

**「戻る/進むで、前に見ていた日へ戻れるようにする」が、期待どおりに
なっていない。** 画面内スクロールでの週移動（`scrollToDate()` /
`moveToMonday()` が `scrollToId()` で完結するケース）は
`replaceDateInUrl()`（`history.replaceState`）で URL だけ書き換えて
おり、**ブラウザの履歴には追加されない。**

実際に確かめた手順（`?date=2021-03-01` を開き、← を 8 回押す）:

```
0 ...?date=2021-03-08  histlen= 2   ← replaceState（画面内で完結）
1 ...?date=2021-03-15  histlen= 2   ← replaceState
2 ...?date=2021-03-22  histlen= 2   ← replaceState
3 ...?date=2021-03-29  histlen= 3   ← doGet（新規ロード、pushで増える）
4 ...?date=2021-04-05  histlen= 3   ← replaceState
5 ...?date=2021-04-12  histlen= 3   ← replaceState
6 ...?date=2021-04-19  histlen= 3   ← replaceState
7 ...?date=2021-04-26  histlen= 4   ← doGet
```

この状態で戻る（`go_back`）を 3 回押すと:

```
back 0: ?date=2021-04-19
back 1: ?date=2021-03-22   ← 期待は 2021-04-12
back 2: about:blank        ← 期待は 2021-03-15
```

**画面内で完結する移動（連続して何度 ←/→ を押しても、既に読み込んで
ある範囲に収まっている限り）は、途中の日付を経由せずに一気に戻って
しまう。** 依頼の「何回か日付を移動して、戻ると前に見ていた日へ戻る」を
そのまま試すと、この症状に当たる（1 回や、範囲外へ出る移動を挟んだ
場合は正しく戻る）。

`src/ytsched/webroot/static/js/my.js` の `replaceDateInUrl()`
（248〜252 行）と、それを呼ぶ `scrollToDate()`（386〜402 行）・
`moveToMonday()`（412〜457 行）が該当箇所。実装報告に「popstate は
拾っていない。`location.href` での遷移も `replaceState` も、戻る/進むは
ブラウザが処理する」とあるが、`replaceState` は履歴を増やさないため、
この前提が成り立っていない。

## 確かめられなかったもの

- **編集画面で ←→ が効かないこと。** `keydown` が `main.html` にしか
  登録されていないことはコードで確認したが、編集画面を開いた状態で
  実際に ←→ を押す確認はしていない
- 削除（`del`）のあとのリロードでの再送信は確かめていない
  （追加・修正のみ確かめた）
- モバイル幅（412px）でのスワイプは TODO-049 の範囲なので確かめていない

## 使ったコマンド（抜粋）

```
mise run test
mise run lint
mise run typecheck
DATADIR=<一時ディレクトリ>
uv run ytsched webapp --datadir "$DATADIR" --port 18085
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18085/ytsched/
env -u DISPLAY uv run --with playwright python <検証スクリプト>
env -u DISPLAY uv run --with playwright python tools/screenshot.py --width 412 --width 800 --open -o <出力先> "http://localhost:18085/ytsched/?date=2026-07-11"
```

## 判断が要る点

「戻る/進む」の挙動（`replaceState` による履歴の欠落）を直すかどうかは
main の判断。`popstate` を拾って `replaceState` されたタイミングでも
再描画する形にするか、画面内移動でも `pushState` にするか、選択肢は
複数ありそう。

---

## 2 回目の確認

`pushDateInUrl()`（`pushState`）＋ `popstateHdr()` への直しと、
検索語・目標件数を `doPost` に戻した直しを確認した。

### 通ったもの

- `mise run test` → 427 passed
- **戻る/進むの、いちばん大きい症状は直っている。** 前回と同じ手順
  （`?date=2021-03-01` を開き、画面内で完結する移動だけ ← を 3 回、
  戻るを 3 回）を繰り返すと、今度は 1 回ずつ正しく辿れた

  ```
  press 0 ?date=2021-03-08
  press 1 ?date=2021-03-15
  press 2 ?date=2021-03-22
  back 0  ?date=2021-03-15  (期待どおり)
  back 1  ?date=2021-03-08  (期待どおり)
  back 2  ?date=2021-03-01  (期待どおり)
  ```

- **検索語・目標件数が URL に載らないこと。** 次のどれでも
  `?date=...` 以外のクエリが付かないことを確かめた
  - 検索語を入れて検索欄の虫眼鏡を押す
  - 検索中にホームボタンを 1 回押す（`homeButtonHdr`）
  - 目標件数（`#search_n_in`）を変える
  - 検索結果の日付欄を押して検索を解除する（同時に検索欄の値も
    空になることを確認）
  - 検索結果の予定を押して編集画面へ移る（`cur_date` などは付くが
    `search_str` は付かない）
- **編集画面で ←→ が効かないこと。** 編集画面を開いた状態で
  ArrowLeft・ArrowRight を押しても URL は変わらなかった
- **削除のあとのリロードで二重に消えたりしないこと。** 削除 → 一覧へ
  リダイレクト → データファイルは 0 行 → リロード x2 でも 0 行のまま
  （ファイルは残るが空。エラーにもならない）
- サーバのログ（`server2.log`）に例外・トレースバックは出ていない

### 見つけたこと（残っている分）

**画面外へ出て `doGet` で読み直しになる移動をまたぐと、戻る/進むが
1 回分ずれる。** ← を 4 回押して（3 回目までは画面内、4 回目で
読み込んである範囲の外に出て `doGet` の新規ロードになる）から戻るを
4 回押すと:

```
press 0 ?date=2021-03-08  histlen 4
press 1 ?date=2021-03-15  histlen 5
press 2 ?date=2021-03-22  histlen 6
press 3 ?date=2021-03-29  histlen 8   ← ここだけ +2（doGet のとき）
back 0  ?date=2021-03-29             ← URL 変わらず（見た目は無反応）
back 1  ?date=2021-03-22
back 2  ?date=2021-03-22             ← また変わらず
back 3  ?date=2021-03-15
```

**原因は `main.html` の `onloadHdr()`。** どのページ読み込みでも
（初回表示だけでなく、`doGet` による読み直しでも）
`scrollToDate(location.pathname, el_date.value, el_sde_align.value,
"instant")` を呼んでおり、これが内部で `pushDateInUrl()` を呼ぶ
（`scrollToDate()` 386〜402 行）。**新規ロードそのものが 1 エントリ、
その直後の `onloadHdr` がもう 1 エントリを積むため、同じ日付が
2 つ並ぶ。** 戻る/進むを 1 回押しても、同じ URL のエントリが 2 つ並ぶので、
見た目が変わらない場面が出る。

該当箇所: `src/ytsched/webroot/static/js/my.js` の `pushDateInUrl()`
（285〜291 行）、`scrollToDate()`（386〜402 行）。呼び出し元は
`src/ytsched/webroot/templates/main.html` の `onloadHdr()`
（89〜90 行、`scrollToDate(location.pathname, ...)`）。

画面内だけで完結する移動（前回・今回とも確かめた基本のケース）は
直っており、症状は軽くなっている。ただし「何回か移動して戻ると
1 つずつ辿れる」を、範囲外への移動を挟んで試すと、まだ崩れる。

### 確かめられなかったもの

- モバイル幅（412px）でのスワイプは TODO-049 の範囲なので、今回も
  確かめていない
- `src/README.md` の書き直しが実際のコードと合っているかは、
  文面の突き合わせをしていない（reviewer の担当と理解している）

### 判断が要る点

`onloadHdr()` が読み直しのたびに `pushDateInUrl()` を重ねて呼ぶ件を
直すかどうか。**画面外への移動をまたいだときだけ発生し、症状は
「戻る/進むを 1 回余分に押す必要がある」程度**で、前回見つけた
「途中の日付を飛び越えて `about:blank` まで行く」ほどではない。
直すなら、`onloadHdr()` 側で「読み直し直後は push しない」形にする
（例えば `pushDateInUrl` の代わりに `replaceState` を使う、または
呼ばない）選択肢がありそう。

---

## 3 回目の確認

`scrollToDate()` の `push_flag`（`onloadHdr()` からは `false`）を効かせた直しを確認した。

### 通ったもの

- `mise run test` → 427 passed
- **前回見つけた「読み直しをまたぐと 1 回分ずれる」症状は直っている。**
  前回と同じ手順（`?date=2021-03-01` を開いて ← を 4 回、戻るを 4 回、
  進むを 4 回）を繰り返した。今回は `histlen` が 1 回の移動ごとに
  必ず +1 で、戻る/進むも 1 回ずつずれずに辿れた

  ```
  after goto+onload, histlen: 2
  press 0 ?date=2021-03-08  histlen 3
  press 1 ?date=2021-03-15  histlen 4
  press 2 ?date=2021-03-22  histlen 5
  press 3 ?date=2021-03-29&sde_align=top  histlen 6   ← 前回は +2 だった箇所
  back 0  ?date=2021-03-22   (期待どおり)
  back 1  ?date=2021-03-15   (期待どおり)
  back 2  ?date=2021-03-08   (期待どおり)
  back 3  ?date=2021-03-01   (期待どおり)
  forward 0 ?date=2021-03-08
  forward 1 ?date=2021-03-15
  forward 2 ?date=2021-03-22
  forward 3 ?date=2021-03-29&sde_align=top
  ```

- **ホームボタン（`homeButtonHdr` の単一クリック）からの移動も、
  今までどおり履歴に積まれる。** 検索していない状態で 1 回クリック →
  `histlen` が +1、URL も変わる。そのあと ← で 1 回移動してから
  もう一度ホームを押しても同様に +1 ずつ増え、戻るで 1 つずつ
  正しく辿れた

  ```
  after goto+onload, histlen: 2
  home click 1 -> ?date=2026-08-25  histlen: 3
  arrow        -> ?date=2026-08-31  histlen: 4
  home click 2 -> ?date=2026-08-25  histlen: 5
  back 0 -> ?date=2026-08-31
  back 1 -> ?date=2026-08-25
  ```

- サーバのログに例外・トレースバックは出ていない

### 確かめられなかったもの

- モバイル幅（412px）でのスワイプは、今回も TODO-049 の範囲として
  確かめていない

これで、依頼にあった「戻る/進む」まわりの指摘（1 回目・2 回目とも）は
解消していることを確認した。
