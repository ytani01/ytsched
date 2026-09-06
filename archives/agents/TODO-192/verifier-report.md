# TODO-192 verifier 報告

## 前提の確認

main が用意した `deny.txt`（33件）/ `allow.txt` を `check.sh` で流した結果は
NG 0（先方の結果を再確認、再実行はしていない）。以下は自分で追加したケース。

## settings.json の書式

- `jq .` で JSON として妥当。○
- `~/.claude/settings.json` の既存 `PreToolUse: Bash` エントリと同じ形
  （`matcher` / `hooks[].type=command` / `command` / `timeout`）。○
- `$CLAUDE_PROJECT_DIR` の使い方も仕様どおり。○

## 誤爆（最優先で見たもの）

依頼の「素通りすべきもの」（mise 全タスク、docs/Developer.md・README・
tests/README.md・CLAUDE.md のコマンド例）はすべて exit 0 で通った
（`uv run pytest tests` / `ruff format|check` / `basedpyright` / `mypy` /
`uv run ytsched {webapp,migrate,fix-id,holiday,notify} --datadir /tmp/x` /
`uv run pytest tests/test_browser.py -v` / `uv run python tests/make_test_data.py` 等、
16件すべて exit 0）。

**新たに見つけた誤爆 2件（exit 2 になってしまう、実際には実データを触らない）:**

1. `printf "%s\n" "~/ytsched/data"` → exit 2
   パスを文字列として印字するだけなのに、`touches_real_data` が
   セグメント全体の文字列一致で判定し、`first` が `printf` は
   読み取り専用の許可リスト（116行目、`echo` はあるが `printf` は無い）に
   入っていないため止まる。
2. `git commit -m "about ~/ytsched/data handling"` → exit 2
   コミットメッセージにパスを書いただけで止まる。`first` が `git` の場合の
   除外が無い。TODO の本文や archives の報告でパスを引用する場面は普通に
   あるので、実際の作業を止める可能性がある。

## 見逃し（実データを書き換えられてしまう、深刻度高いもの）

読み取り専用として許可リストに入っている `echo` / `cat` / `find` は、
リダイレクトや `-delete` を伴うと書き込み・削除になるが、判定は
`first` の語だけを見ているため素通りする。

- `echo x >> ~/ytsched/data/f.jsonl` → exit 0（実データに追記できてしまう）
- `cat /tmp/x > ~/ytsched/data/f.jsonl` → exit 0（実データを上書きできてしまう）
- `find ~/ytsched/data -name "*.bak" -delete` → exit 0（実データを削除できてしまう）

## バイパス（静的解析の限界。既知にしてよいかは要判断）

- `bash -c "mise run upgradeproject"` → exit 0（`first` は `bash` で、
  ネストした文字列の中身は見ない）
- `$(echo mise) run upgradeproject` → exit 0（コマンド置換でコマンド名を
  組み立てると `first` が `$(echo` になり一致しない）
- `cd ~ && cat ytsched/data/x`（`~/` を付けない相対パス）→ exit 0
  これはスクリプトのコメント（20-21行）で明示的に「ただの
  `ytsched/data` では見ない」と書かれた既知の割り切りなので、
  新規の不具合ではなく確認のみ。

## スクリプトの実装バグ

`guard-bash-ytsched.sh` 161-162行目の `printf` が、書式文字列の先頭が
`--datadir` で始まるため、bash 組み込みの `printf` がオプションと
誤認して失敗する。

```
/…/guard-bash-ytsched.sh: 161 行: printf: --: 無効なオプションです
```

exit コード自体は 2 のまま通るので「止める」動作は壊れていないが、
利用者に見せるはずのメッセージが表示されず、代わりに printf のエラーが
出る（`--datadir の無い ytsched の起動は…` という説明が一切出ない）。
`printf -- '...'` にするか、書式の先頭に `--` を置かない書き方に直す必要が
ある。133-134行目・96-98行目の printf は先頭が `--` でないため無事。

## まとめ

- 依頼にあった「正しい書き方の素通り」は該当ケースで問題なし。
- ただし `printf` でパスを文字列として使う、`git commit -m` でパスに
  言及する、という**日常的にありそうな書き方が誤爆する**（優先度高）。
- `echo >>` / `cat >` / `find -delete` による実データの書き換え・削除が
  素通りする（フックの主目的である「実データを書き換えから守る」が
  部分的に成立していない）。
- 161-162行目の `printf` の実装バグ（メッセージが出ない）。
- `bash -c` や `$()` によるバイパスは静的解析の原理的な限界。
  対応するかは main の判断（どこまで作り込むかのトレードオフ）。

## 再確認（修正後）

### 前回の 5 件

1. 実装バグ（`printf` の `--` 誤認）→ **解消。** 説明メッセージが正しく出る
   ようになった（`printf -- '...'`）。
2. 誤爆 `printf "%s\n" "~/ytsched/data"` → **解消**（exit 0）。
3. 誤爆 `git commit -m "about ~/ytsched/data handling"` → **解消**（exit 0）。
4. 見逃し `echo x >> ~/ytsched/data/f.jsonl` / `cat /tmp/x > ~/ytsched/data/f.jsonl`
   → **解消**（exit 2、「リダイレクトで書き込もうとしている」）。
5. 見逃し `find ~/ytsched/data -name "*.bak" -delete` → **解消**（exit 2、
   `find -exec` も同様に exit 2 を確認）。

5 件とも解消を確認した。

### 新しい誤爆

依頼にあった `deny.txt`（17件）/ `allow.txt`（24件）の中身は個別に再現していない
（main が NG 0 を確認済みのため）。自分で足したケースの中で、意図どおり
通るべきものが誤って止まる例は見つからなかった。

### 新しい見逃し（`git` 許可・リダイレクト判定の抜け）

**`git` を読み取り専用の許可リストに無条件で加えたことで、実データを
書き換える `git` サブコマンドも素通りする**（exit 0、すべて実データを
変更・削除しうる）:

- `git -C ~/ytsched/data commit -am "x"`
- `git rm ~/ytsched/data/f.jsonl`
- `git checkout -- ~/ytsched/data/f.jsonl`
- `git -C ~/ytsched/data clean -fd`

`sed` / `find` は個別のフラグ（`-i` / `-delete` 等）で書き込みを判定して
いるが、`git` だけはサブコマンドを見ずに丸ごと許可している。`~/ytsched/data`
が git 管理下に無ければ実害は無いが、その前提はスクリプト中に書かれていない。
（`git add` は index を触るだけで作業ファイルは変えないので実害なし。）

**リダイレクト判定に抜けがある**（fd 番号つき・空白なしの書き方が
判定を素通りする、いずれも exit 0）:

- `echo x 1> ~/ytsched/data/f.jsonl`（`1>` は `'>'` / `'>>'` の完全一致にも
  `'>'*` にもマッチしない）
- `echo x 2> ~/ytsched/data/f.jsonl`（同様。ただし stderr への書き込みなので
  実害は小さい）
- `echo x>>~/ytsched/data/f.jsonl`（`x` と `>>` の間に空白が無く、
  `read -a` が `x>>~/ytsched/data/f.jsonl` を 1 語として扱うため、
  `'>'` / `'>>'` の完全一致にも `'>'*` にもマッチしない）

一方、`>|` / `&>` / `tee` 経由は確認した範囲では正しく exit 2 になった
（`&>` は `&` がセグメント区切りに使われている副作用で通っている面がある）。

### まとめ

前回指摘した 5 件はすべて解消を確認した。新たに、`git` の無条件許可と
リダイレクト判定の抜け（`1>` / `fd無し空白無し>>`）による見逃しを見つけた。
どちらも「実データを書き換えから守る」という主目的に関わるため、
対応するかどうかは main の判断を仰ぎたい。

## 再々確認（2 回目の修正後）

### 2 回目に挙げた見逃し 2 種

- `git` の無条件許可 → **解消。** `git -C ~/ytsched/data commit`・
  `git rm`・`git checkout --`・`git -C ~/ytsched/data clean -fd` はすべて
  exit 2 になった。`git log --`・`git commit -m "<path>"`・`git add` は
  意図どおり exit 0（通る）。
- リダイレクト判定の抜け（`1>` / `2>` / 空白なし `x>>path`）→ **解消。**
  3 件とも exit 2 で「リダイレクトで書き込もうとしている」になった。

1 回目・2 回目で解消済みとした項目（`printf` のメッセージ表示、
`echo >>`、`find -delete`、`mise run upgradeproject`、
`--datadir` 無しの `uv run ytsched webapp`）も再確認し、いずれも
戻っていない（意図どおり）。

### リダイレクト判定を文字列走査にしたことによる誤爆（(a)）

見つからなかった。以下はいずれも意図どおり exit 0（誤爆なし）:

- `grep "a > b" ~/ytsched/data/f.jsonl`（クォート内の `>` に反応しない）
- `echo "value ~/ytsched/data/f is fine" > /tmp/out.txt`
  （文中に実データのパスが出てきても、実際のリダイレクト先が `/tmp` なら通る）
- `echo "note: see ~/ytsched/data for details, also > check this"`
  （文中の `>` の直後が実データのパスでなければ通る）
- `cat ~/ytsched/data/f.jsonl > /tmp/out.txt`（読み取り＋別先への書き出し）

参考までに `awk '{print > "/tmp/x"}' ~/ytsched/data/f.jsonl` は exit 2 だが、
これは `awk` がそもそも読み取り専用の許可リストに無いために既定で
止まっているだけで、今回のリダイレクト判定の変更とは無関係（1 回目から
変わっていない挙動）。

### git のサブコマンド判定（(b)）

- `git --no-pager log -- ~/ytsched/data/f.jsonl` → exit 0（意図どおり）
- `git -c core.x=y commit -m "x" ~/ytsched/data/f.jsonl` → exit 0
  （結果は正しいが、下記のとおり判定は名目上ズレている）
- `git submodule status ~/ytsched/data` → exit 0（意図どおり、読み取り）

**新しい見逃しを 1 件見つけた。** `git -c core.x=y rm ~/ytsched/data/f.jsonl`
→ **exit 0（本来は止めたい `git rm` が素通りする）。**

原因: サブコマンド判定のループは `-*` で始まる語だけを「フラグ」として
読み飛ばすが、`-c <value>` のように値を別の語として取る書き方では、
その値（`core.x=y`）が `-` で始まらないため「サブコマンドが来た」と
誤認してループを抜けてしまい（155行目の `*) break`）、本当のサブコマンド
`rm` を見ないまま通ってしまう。`-c core.x=y log` のように無害な
サブコマンドの場合は結果的に問題にならないが、`-c core.x=y rm` /
`-c core.x=y checkout -- <file>` のように値を取るオプションの後ろに
危険なサブコマンドを置くと素通りする。`git -C` は値が同じ語にあっても
別語にあっても直接パターンで拾えているので影響が無いが、`-c` は同様の
直接パターンが無い。

`git submodule` 自体は rm/mv/clean 等のリストに無いため、
`git submodule deinit ~/ytsched/data` のような単発コマンドでの
書き換えは（試していないが）ロジック上は素通りする可能性が高い。
実害の大きさは `-c` の抜けより小さいと見て、参考情報として記載するに留める。

### まとめ

2 回目に挙げた 2 件は解消を確認した。文字列走査によるリダイレクト判定の
誤爆は見つからなかった。`git` のサブコマンド判定に、`-c <value>` のように
フラグと値が別語になる書き方で危険なサブコマンドを見逃す抜けを 1 件
新たに見つけた（`git -c core.x=y rm <実データ>` が通る）。対応するかは
main の判断。

## 最終確認

### 3 回目の指摘 2 件

- `git -c core.x=y rm ~/ytsched/data/f.jsonl` → **解消**（exit 2、
  「git rm で書き換えようとしている」）。`-c a=b -c c=d checkout --` の
  ように `-c` を重ねても正しく値を 2 語ずつ飛ばして `checkout` を検出した。
- `git submodule deinit ~/ytsched/data` → **解消**（exit 2、
  「git submodule で書き換えようとしている」）。

追加の deny 側 `git --no-pager clean -fd ~/ytsched/data` も exit 2。
allow 側 `git -c core.x=y commit -m "about ~/ytsched/data"` /
`git --no-pager log -- ~/ytsched/data/f.jsonl` /
`git diff -- ~/ytsched/data/f.jsonl` はいずれも exit 0（意図どおり）。

### 1〜3 回目で解消済みとした項目の再確認（リグレッションなし）

以下を今回のスクリプトで再実行し、すべて前回と同じ結果だった。

- `printf` のメッセージ表示（`--` の誤認なし）
- `echo x >> ~/ytsched/data/f.jsonl` / `find ... -delete` → exit 2
- `--datadir` 無しの `uv run ytsched webapp` → exit 2
- `mise run upgradeproject` → exit 2
- `git log` / `git commit -m` / `git add`（パスに言及するだけ） → exit 0
- リダイレクトの文字列走査（`1>` `2>` 空白なし `>>`、クォート内の `>` に
  反応しない）→ 前回と同じ

戻っている項目は無い。

### 残る懸念（新しいケース探しではなく、作りそのものについて）

**セグメント分割がクォートを見ていないため、引用符の中の `;` `|` `&`
`&&` `||` が実際のシェル演算子と区別されない。** 61 行目の
`sed -e 's/&&/\n/g' ...` は文字列としての置換で、クォートの中身も
容赦なく割ってしまう。これにより、**実際には安全なコマンドが誤って
止まるケースが再現できた**:

```
echo "a; rm -rf ~/ytsched/data" | cat
```

このコマンドは実際には `rm` を実行しない（クォートの中の文字列を
`echo` して `cat` に渡すだけ）。しかし `;` で分割され、
`rm -rf ~/ytsched/data` という単独のセグメントに見えてしまい、
`git`/`sed`/`find` 以外の既定の deny 経路（190-192行目）で
exit 2 になる。

同じ仕組みの裏側（分割によって危険な内容が安全に見えるセグメントへ
分散し、素通りする方向）も原理的にはあり得るが、今回はそこまでは
再現できていない。

これは `bash -c` / `$()` バイパスや相対パスの割り切りとは性質が違う。
それらは**回避しようとする側**が使う書き方だが、こちらは**善意の
コマンドがクォートの中でたまたま `;` や実データっぽい文字列を含むだけで
誤爆しうる**。頻度は高くないと思われるものの、対応しないと決めるにしても、
`bash -c` 等と同列の「既知の割り切り」としてスクリプト冒頭のコメントに
書き足しておくと、次に見た人が「見落とし」と「割り切り」を区別しやすい。

その他、設計上のトレードオフとして認識しておいたほうがよい点:

- `jq` が使えない環境では `cmd=$(jq ...) || exit 0` により**フックが
  無言で無効化される**（fail-open）。安全側（誤って止めない）に倒す
  設計としては妥当だが、無効化されたこと自体は利用者に見えない。

### まとめ

3 回目の指摘 2 件は解消し、1〜3 回目の解消済み項目にリグレッションは
無い。新たに見つけた懸念は、クォート内の区切り文字を実際の演算子と
区別しない設計に起因する誤爆 1 種類（`echo "a; rm -rf <実データ>" | cat`
のような書き方で発生）。対応するか、割り切りとして明記するに留めるかは
main の判断。
