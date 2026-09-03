# TODO-171 implementer への依頼

## 目的

`sde_id` の末尾にバージョン番号（版）を付け、編集した予定と、そのとき
ゴミ箱に入った古い内容の対応が分かるようにする。

`TODO.md` の TODO-171 の節を先に読むこと。ここにはそこへ書き切れなかった
実装の詳細を書く。**仕様は確定済み。相談せずにこのとおり実装する。**

## ID の形式

`{UUID}-{版}`。UUID は小文字ハイフン付き 36 文字。版は 1 から始まる
10 進の整数で、**ゼロ埋めしない**（`1`, `2`, … `10`, … `1000`）。

例: `3f2a1b0c-4d5e-6f70-8192-a3b4c5d6e7f8-1`

## 1. `SchedDataEnt`（`src/ytsched/ytsched.py`）

ID を扱うクラスメソッドを足す。正規表現は**この形だけ**を通す
（`fix_id.py` の `UUID_PATTERN` と同じ厳しさ）。

```python
SDE_ID_PATTERN = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    r"-([1-9][0-9]*)$"
)
```

- `split_id(sde_id) -> tuple[str, int] | None`
  — UUID 部分と版に分ける。形式が違えば `None`
- `id_uuid(sde_id) -> str`
  — 版を除いた UUID 部分。形式が違えば `sde_id` をそのまま返す
- `id_version(sde_id) -> str`
  — 版の文字列（`"1"`）。形式が違えば `""`
- `format_id(uuid_part, version) -> str`
  — `f"{uuid_part}-{version}"`
- `next_id(sde_id) -> str`
  — 次の版の ID。**形式が違えば `new_id()` を返す**（旧形式の ID は
  `fix-id` で振り直す前提。中途半端な形を作らない）
- `new_id()` は `format_id(str(uuid.uuid4()), 1)` を返すように変える

`split_id()` を通さずに文字列を切り貼りしないこと。UUID の最後の区切りが
偶然 12 桁の数字になることがあり、単純な「末尾の `-数字`」では
版のない UUID を誤って分解する。UUID 部分まで含めて見れば、
ゼロ埋めが無くても曖昧にならない。

先頭のゼロは通さない（`[1-9][0-9]*`）。`-001` のような書き方は
新しい形式と見なさず、`fix-id` が振り直す。

## 2. 編集で版を増やす（`src/ytsched/sched_update.py`）

`SchedUpdater.exec_update()` で、`cmd` が `fix`/`update` のとき、
**ゴミ箱へ入る側（`cmd_del()`）は元の ID のまま**、
**新しく作る側（`cmd_add()`）は `next_id()` の ID**にする。

`try` の前で追加用の ID を決めておく:

```python
add_sde_id = sde_id
if cmd in ["fix", "update"] and sde_id:
    add_sde_id = SchedDataEnt.next_id(sde_id)
```

複製を含む `add` は、いまどおり `sde_id = None` のままで、
`SchedDataEnt` が `new_id()` を発行する（新しい UUID の `-1`）。

## 3. ゴミ箱からの復活（`src/ytsched/trash_handler.py`）

`_restore()` はいま新しい UUID を発行している（TODO-086）。これを
**元の UUID を引き継いで版を増やす**ように変える。

版の決め方 — **ゴミ箱と、復活先の日付のファイルの両方**を見て、
同じ UUID を持つ行の最大の版 + 1 にする。片方にしか無ければそちらだけ、
どちらにも無ければ、復活させる行の版 + 1。

- ゴミ箱側は `TrashFile` に `max_version(uuid_part) -> int` を足して数える
  （同じ UUID の行が無ければ 0）
- 復活先は `self._sd.get_sdf(restored.date).sde` を見る
- 元の ID が新しい形式でなければ（旧形式のまま）、いまどおり
  新しい ID（`sde_id=None`）にする

両方を見るのは、ID が重複しないようにするため。編集のたびに
古い側がゴミ箱へ入るので、生きている予定の版はゴミ箱の最大 + 1 になる。
ゴミ箱だけを見て + 1 すると、生きている予定と同じ ID になる。

タイトルの先頭に `(復活)` を付けるのは、いまのまま変えない。

## 4. ゴミ箱の絞り込みとグループ化

- `TrashFile.entries(sde_id=...)` の絞り込みを、**版を除いた UUID 部分の
  一致**にする（`SchedDataEnt.id_uuid()` どうしを比べる）。版が変わっても
  古い行が出るようにするため
- `TrashFile.get(sde_id, trashed_at)` は**完全一致のまま**にする。
  `entries()` の絞り込みが緩くなるので、`get()` の側で
  `entry.sde.sde_id == sde_id` も見ること
- `TrashFile.delete_many()` も完全一致のまま（変更なし）
- `TrashHandler.get()` のグループ化のキーを `SchedDataEnt.id_uuid()` にする

## 5. 画面に版を出す

`TrashEntry` に版を返すプロパティを足す:

```python
@property
def version(self) -> str:
    """版（``"1"``）。ID が新しい形式でなければ ``""``"""
```

`trash.html` の、削除時刻を出している行（末尾の `my-fs-x-small`）で、
版があるときだけ前に付ける:

```html
{% if entry.version %}版 {{ entry.version }} ・ {% end %}
```

グループの見出し（`同じ予定の内容が N 件`）は変えない。

## 6. `fix-id`（`src/ytsched/fix_id.py`）

新しい形式へ揃えるツールに変える。

- 対象に **`trash.jsonl` を加える**（TODO-170 では対象外にしていた）。
  `{年}/{月}/{日}.jsonl`・`ToDo.jsonl`・`trash.jsonl` の 3 つ。
  `.cgi`・`.bak` は対象外のまま
- 1 行ごとの判定:
  - 既に `{UUID}-{版}` の形（`split_id()` が通る）→ そのまま
  - UUID の形（`is_uuid()`）→ **UUID は保って** `-1` を付ける
  - それ以外 → 新しい UUID の `-1`
- `trash.jsonl` の行は `trashed_at` が先頭にあるが、`sde_id` だけを
  差し替えるので、いまの実装のままキーの並びは保たれる
- ゴミ箱の行も 1 行ずつ独立に振り直す。**旧形式だった予定は、
  ゴミ箱の行と現在の予定が繋がらない**。既に UUID が一致していた行も
  両方が `-1` になって版では区別できない。**ここは割り切る**
  （利用者の了承済み。直そうとしないこと）
- `FixIdStat.lines_already_uuid` は `lines_already_ok`（元から新しい形式
  だった行）に改名し、出力の文言も合わせる
- 読めない行・`sde_id` が無い行・空行の扱いは、いまのまま変えない
- 冒頭の docstring は、`trash.jsonl` を対象外と書いてあるところを含めて
  書き直す

## 7. テスト

- `tests/test_ytsched.py` — `new_id()` の形、`split_id()`/`id_uuid()`/
  `id_version()`/`next_id()`。**最後の区切りが 12 桁の数字の UUID**を
  誤って分解しないことも見る。`-001` のようなゼロ埋めを新しい形式と
  見なさないことも見る
- `tests/test_fix_id.py` — 3 通りの判定、`trash.jsonl` が対象に入ること、
  既に新しい形式の行は書き換えないこと（ファイルを書かないこと）
- `tests/test_trash.py` — UUID 部分での絞り込み、`get()` の完全一致、
  `max_version()`
- 編集で版が増えること、復活で UUID を引き継いで版が増えることを、
  ハンドラのテスト（`tests/test_main_handler.py` /
  `tests/test_handler.py` のうち合う方）に足す

`tests/README.md` に各テストファイルの役割があるので、置き場所は
それに合わせる。テストデータの作り方は `tests/helpers.py` を見る。

## 8. 文書

- `docs/data-format.md` の `sde_id` の行（54 行目付近）— 新しい形式と、
  編集で版が増えることを書く。`fix-id` の説明も直す
- `docs/data-format.md` のゴミ箱の節（145 行目付近）— 復活が UUID を
  引き継ぐようになったことを書く
- `docs/data-format.md` の実データの統計の節（241 行目付近）— `fix-id` の
  説明を新しい形式に合わせる
- `docs/Install.md`（141 行目付近）・`docs/Developer.md`（128 行目付近）
  — `fix-id` の説明を新しい形式に合わせる。`trash.jsonl` も対象に
  なったことを書く
- `src/README.md` の 25 行目（`fix_id.py` の説明）、98 行目付近
  （`SchedDataEnt` の `sde_id`）
- **利用者向けの文書（`README.md`・`docs/User.md`・`docs/Install.md`）には
  TODO 番号を書かない**

## やらないこと

- `sde_id` を JSON の別のキーに分けない（版は ID の文字列の一部）
- 既存データの移行の道具を増やさない（`fix-id` だけ）
- `TODO.md` のチェックボックスは触らない（main が付ける）

## 完了条件

- `mise run fmt` / `typecheck` / `lint` / `test` が通る
  （`mise run upgradeproject` は**走らせない**）
- 変更点・確認したこと・残る懸念を
  `archives/agents/TODO-171/implementer-report.md` に書く

返事は「終わったか・報告ファイルのパス・判断が要る点」を 5 行以内で。
