# TODO-077 implementer への依頼

`TODO.md` の TODO-077 と `docs/design-review.md` の B を先に読むこと。

## 決まっていること（main が決めた。蒸し返さない）

**`exec_update()` 一式は `main_handler.py` に置いたままにする。**
前半が tornado の `get_argument()` に依存していて、`SchedData` を受け取る
クラスへ出すには、フォームの値の取り出しと変換を先に分けなければならない。
それは TODO-081 の範囲なので、この項目では `.bak` の修正だけをやる。

## やること

1 回の更新（`fix`・`update`・`add`・`del`）で、同じデータファイルの
`save()` が 1 回になるようにする。

1. `src/ytsched/ytsched.py` の `SchedData.add_sde()` / `del_sde()` から
   `sdf.save()` を外す。代わりに「変更のあった日付」を `SchedData` 側に
   覚えさせる（`None` は ToDo なので、日付の集合に `None` が入る点に注意）
2. `SchedData` に `save()` を足す。覚えている日付の `SchedDataFile` を
   **1 つにつき 1 回だけ** `save()` し、覚えている集合を空にする
3. `src/ytsched/main_handler.py` の `exec_update()` で、`cmd_del()` /
   `cmd_add()` を呼び終えたあとに `self._sd.save()` を 1 回呼ぶ。
   途中で 400 を投げる経路（`get_date_arg()` など）は、そもそも
   `cmd_*` より前なので触らなくてよい
4. docstring を直す。`add_sde()` / `del_sde()` の「保存する」という
   前提が変わるので、**呼んだだけでは保存されない**ことを書く。
   なぜ分けたか（TODO-077）も 1 行添える

## 気をつけること

- `SchedData.add_sde()` / `del_sde()` を呼んでいるのは
  `src/ytsched/main_handler.py` の `cmd_add()` / `cmd_del()` と、
  `tests/test_ytsched.py` の 3 つのテストだけ。grep で確かめてから直すこと
- `SchedDataFile.save()` 自身は変えない。空のファイルをバックアップしない
  決まり（TODO-005）はそのまま
- `fix` で日付が変わる場合（`orig_date` と `date` が違う）は、
  **別々のファイルなので save は 2 回**でよい。1 ファイルにつき 1 回、が
  守れていればよい
- 例外で途中で抜けたときに「変更が保存されない」ことになるが、
  今までも中途半端に保存されていたので悪化ではない。手当ては要らない

## テスト

`tests/README.md` を読み、既存のやり方に合わせる。

- `tests/test_ytsched.py` の `SchedData` 系のテスト 3 つが、保存を
  切り離したことで通らなくなるはず。`sd.save()` を呼ぶように直す。
  **「保存されること」を見ているテストを消さない**
- 新しく足すもの:
  - `SchedData.add_sde()` / `del_sde()` を呼んだだけではファイルが
    変わらず、`save()` で書かれること
  - **同じ日に 2 件（A・B）あるファイルで B を `fix` したとき、
    `.bak` に A・B の両方が残ること。** これがこの項目の本題。
    HTTP 経由（`tests/test_web.py` の POST）で見るのが望ましい。
    既存の `fix` のテストの近くに置くこと
  - 同じ日に 2 回 `add` したときなど、`save()` が 1 回で済むこと
    （見るのが難しければ省いてよい。報告に書くこと）

`mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
**`mise run upgradeproject` は走らせないこと。**
アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する。
