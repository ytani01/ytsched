# TODO-192. ytsched 固有のコマンドを PreToolUse フックで止める

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | medium | 36,730 | 84,913 | 83% |
| verifier | Sonnet 5 | medium | 11,878 | 83,043 | 17% |
| 合計 |  |  | 48,608 | 167,956 | 概算 $3.7 |

- verifier は定義（`.claude/agents/verifier.md`）のまま sonnet / medium。上書きしていない
- main のモデルは見込みの Sonnet 5 ではなく Opus 5 だった（利用者の設定）
- 分担の記録は [archives/agents/TODO-192/](../agents/TODO-192/README.md)

## きっかけ

`~/.claude/hooks/guard-bash.sh` が、裸の `cp` / `mv` / `rm` と `git push` を
止めている。同じやり方で、このプロジェクトでしか意味の無いものも止められる。

止めたかったのは 2 つ。

| 止めるもの | 根拠 |
|---|---|
| `~/ytsched/data` を書き換えるコマンド | 起動確認では `--datadir` に一時ディレクトリを渡す |
| `mise run upgradeproject` / `uppj` | 担当には走らせない（TODO-022） |

## やったこと

`.claude/hooks/guard-bash-ytsched.sh` を作り、`.claude/settings.json` の
`hooks.PreToolUse` に `matcher: "Bash"` で登録した。パスは
`$CLAUDE_PROJECT_DIR` 起点。

**名前をユーザー全体側と変えた**（`guard-bash.sh` ではなく
`guard-bash-ytsched.sh`）。同名だと、どちらの話をしているのか分からなくなる。

止めるのは 3 つ。

1. `mise run upgradeproject` / `uppj`（`mise uppj` の形も）
2. `~/ytsched/data` を読み取り以外で触るコマンド
3. `--datadir` の無い ytsched の起動（`uv run ytsched webapp`、
   `mise run webapp` / `web` / `migrate`）。`mise.toml` のこの 3 タスクは
   `--datadir` を渡しておらず、既定の実データを使う

`--help` / `-h` / `--version` は通す。

### 判定の作り

骨格（ヒアドキュメントの本文を落とす、区切りごとに先頭の語を見る）は
`~/.claude/hooks/guard-bash.sh` から流用し、**判定は写していない**。
`PreToolUse: Bash` はユーザー全体側とプロジェクト側の両方が独立に走るので、
写すと二重管理になる。

実データの検出は `~/` `$HOME/` `${HOME}/` `/home/ytani/` 起点だけを見る。
ただの `ytsched/data` では見ない（`--datadir /tmp/xxx/ytsched/data` を
巻き込まないため）。

読み取りだけのコマンド（`ls` `cat` `grep` など）は通し、書き換えるものは
個別に判定する。

| コマンド | 止める条件 |
|---|---|
| リダイレクト | `>` の右側が実データ（`1>` `2>` `&>` `>\|` `>>`、空白なしの `x>>path` も） |
| `sed` | `-i` / `--in-place` がある |
| `find` | `-delete` / `-exec` / `-execdir` / `-ok` / `-okdir` がある |
| `git` | サブコマンドが `rm` `mv` `clean` `checkout` `restore` `reset` `apply` `stash` `submodule`、または `-C` / `--work-tree` がある |
| それ以外 | 読み取り専用の一覧に無ければ止める |

`git` は、コミットメッセージや検索語にパスを書くだけなら通す必要がある。
`-c` のように値が次の語にあるフラグは、値ごと飛ばす（飛ばさないと値を
サブコマンドと見て抜ける）。

### 見ないと決めたもの

いずれもスクリプト冒頭のコメントに書いた。

- **`bash -c "..."` や `$(echo mise) run ...` のバイパス。** 事故を防ぐための
  フックであって、回避しようとする相手を止めるものではない。作り込むと誤爆が増える
- **`~/` を付けない相対パス**（`cd ~ && cat ytsched/data/x`）。実データの検出を
  `$HOME` 起点に限った結果
- **クォートの中の `;` `|` `&` による誤爆**（`echo "a; rm -rf ~/ytsched/data"`）。
  正しく解釈するにはシェルのパーサが要る。止まっても理由は表示されるし、
  書き方を変えれば通る

## テスト

判定を叩くケースを `deny.txt`（29 件）/ `allow.txt`（33 件）に分け、
`check.sh` で exit code を突き合わせた。実データには一切触っていない。

**コマンド文字列に `~/ytsched/data` を含めると、それを叩く Bash 呼び出し自体が
このフックに止まる。** ケースをコマンドラインに直接書くと作業が進まないので、
ファイルに分けている。

素通りすることを確かめたもの: `mise.toml` の全タスク（止める 4 つ以外）、
`docs/Developer.md` / `README.md` / `tests/README.md` / `CLAUDE.md` の
コマンド例、`uv run ytsched <サブコマンド> --datadir /tmp/x`、
`ls` / `cat` / `grep` での実データの読み取り、`git log|status|commit|add|diff`。

止める 3 経路のメッセージは、exit code とは別に目視した。

## 分担の振り返り

**verifier は 4 回で 10 件を挙げ、そのうち 9 件を直した。**

| 回 | 挙がったもの |
|---|---|
| 1 | `printf` の実装バグ、誤爆 2（`printf` / `git commit -m`）、見逃し 3（`echo >>` / `cat >` / `find -delete`）、バイパス |
| 2 | `git` の無条件許可、リダイレクト判定の抜け（`1>` / 空白なし `>>`） |
| 3 | `git -c core.x=y rm`（値付きフラグの後ろが読めていない） |
| 4 | クォート内の区切りによる誤爆 |

**main が一度も自力で見つけられなかったのは、`printf` の書式文字列が `--` で
始まってオプションと誤認される件。** exit code だけを見て、メッセージを
表示させていなかったため。**exit code と出力は別に確かめる。**

**見込みと食い違ったのは、やり取りの回数。** 1 往復で済むつもりが 4 回になった。
原因は、main が**判定を足すときに片方向しか試さなかった**こと。誤爆を潰すために
`git` を許可リストへ丸ごと入れ、その反対側（見逃し）を試していない。
**許可リスト方式は 1 つ足すたびに反対側へ穴が空くので、`deny` と `allow` の
両方にケースを足してから直す。**

**次に同じ規模のフックを書くなら、同じ組み方（main + verifier）でよいが、
verifier への最初の依頼にケース表を作らせる。** 今回は main がケースを作り、
verifier がそれに足す形にしたので、main の想定の外が 4 回に分かれて出てきた。
**先に verifier だけにケースを列挙させ、それを満たす実装を main が書けば、
往復は減らせたはず。** 料金の 83% は main で、その大半は往復で積んだもの。
