# implementer への依頼 (TODO-104)

## やること

週パネルの月間ミニカレンダー (TODO-103) を、画面のスイッチで
出したり消したりできるようにする。

## 仕様（main が決めた。相談せずこのとおりに）

### 設定の持ち方

- `conf.json` のキー `MonthCal`。`"1"` = 出す、`"0"` = 出さない。
  既定は出す（キーが無いとき・読めない値のときは出す）。
- `MainHandler` に `CONF_KEY_MONTH_CAL = "MonthCal"` を足す。
- 他の 4 つ（`SearchStr` / `FilterStr` / `ToDo_Days` / `SearchN`）と同じく
  `update_conf_args()` / `update_conf_arg()` の仕組みに載せる。
  リクエスト引数の名前は `month_cal`。`ConfArgs` に `month_cal: bool` を
  足して、5 つ目として返す。`empty_is_given` は `False`
  （空文字で消えないように。`todo_days` と同じ）。
  `convert` は `"1"` → `True` / `"0"` → `False` にする関数を新しく書く。
  **それ以外の値は `ValueError`** にして、`conf.json` へ保存させない
  （不正な引数の扱いは TODO-027 と同じ）。
- 保存されるのは `update_conf_arg()` が「変換後が str でなければ元の
  文字列」を書く既存の道に乗るので、`"1"` / `"0"` がそのまま入るはず。
  ここは実際に確かめること。

### サーバ側

- `get()` で読んだ値を `mk_weeks()` へ渡し、出さないときは
  `SchedWeek.month_cals` を空リストにする（`load_month_cal()` を
  **呼ばない**。`stat()` の回数を減らすため）。
- `render()` に `month_cal=<bool>` を渡す。テンプレートは
  `w.month_cals` の空・非空ではなく、この値でスイッチの状態を出す。
- 検索モードでは、今までどおりミニカレンダーもスイッチも出さない。

### 画面

- スイッチは、ミニカレンダーの並び (`.my-mini-cal-row`) の**左上**、
  日曜日の日付欄の下あたり。`justify-content: center` のまま
  テーブルを中央に置きたいので、行を `position: relative` にして
  スイッチを `position: absolute; left: …; top: 0` で置く。
- 見た目は、既存のアイコン (`icons/icons.svg`) の `#check-square`
  （出しているとき）と `#square`（出していないとき）を小さく出す。
  他のアイコンの出し方は `main.html` の既存の `<svg><use href=…>` に
  倣う。押せることが分かるよう `my-btn` を付ける。
- 押したときは `doPost()` で、`date` にその週パネルの月曜
  （`w.monday`）、`month_cal` に反転した値 (`'0'` / `'1'`) を送る。
  `main.html` の既存の `doPost(...)` の書き方に倣うこと。
- **出していないときも、スイッチは必ず残す**（戻せなくなるため）。
  ミニカレンダーが無いぶん、行の高さが潰れてスイッチが押しにくく
  ならないようにする。
- 幅 412px（手持ちの端末）で横スクロールが出ないこと。

## テスト

- `str2month_cal`（名前は任せる）の単体テスト: `"1"` / `"0"` /
  それ以外が `ValueError`。
- HTML のテスト（`tests/` の既存の週間表示のテストに倣う）:
  - 既定（`conf.json` に `MonthCal` が無い）でミニカレンダーが出て、
    スイッチも出る。
  - `month_cal=0` を渡すとミニカレンダーが消えて、スイッチは残る。
  - `conf.json` に `"MonthCal": "0"` があるとき、引数なしでも消えている。
  - 切り替えたあと `conf.json` に保存されている。
  - 検索モードではスイッチもミニカレンダーも出ない。

## 前提

- コードを触る前に `src/README.md` と `tests/README.md` を読むこと。
- `mise run fmt` / `lint` / `typecheck` / `test` は叩いてよい。
  `mise run upgradeproject` は**叩かない**。
- 起動して確かめるときは `--datadir` に一時ディレクトリを指定する。

## 報告

`archives/agents/TODO-104/implementer-report.md` に書く。
返事は 5 行以内で、終わったか・報告ファイルのパス・判断が要る点だけ。
