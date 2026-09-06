#!/usr/bin/env bash
#
# PreToolUse(Bash) の hook。ytsched でしか意味の無い 2 つを止める（TODO-192）。
#
#   - ~/ytsched/data（実データ）を触るコマンド
#     起動確認では --datadir に一時ディレクトリを渡す決まり
#   - mise run upgradeproject / uppj
#     呼ぶたびに依存を上げ直すので、担当には走らせない（TODO-022）
#
# 裸の cp / mv / rm と git push は ~/.claude/hooks/guard-bash.sh が止める。
# どのプロジェクトでも要るものなので、こちらには写さない。
# PreToolUse: Bash はユーザー全体側とプロジェクト側の両方が独立に走る。
#
# stdin に Claude Code が渡す JSON を受け取り、止めるときは exit 2 で返す。
# exit 2 のとき、stderr は Claude に渡る（利用者にも表示される）。
#
# 判定の考え方（骨格は ~/.claude/hooks/guard-bash.sh と同じ）:
#   - ヒアドキュメントの本文は中身であってコマンドではないので、先に取り除く
#   - 区切り（改行 ; | & && ||）ごとに、先頭の語だけを見る
#   - 実データの検出は $HOME 起点の書き方だけを見る。ただの `ytsched/data`
#     では見ない（--datadir /tmp/xxx/ytsched/data を巻き込まないため）
#   - `bash -c "..."` や `$(echo mise) run ...` のように、ネストした文字列や
#     コマンド置換でコマンド名を組み立てると、先頭の語が一致せず素通りする。
#     これは事故を防ぐための hook であって、回避しようとする相手を止める
#     ものではない。作り込むと誤爆が増えるので、そこは見ない（TODO-192）
#   - 区切りの判定はクォートを見ないので、`echo "a; rm -rf ~/ytsched/data"`
#     のように、クォートの中に `;` `|` `&` とパスを書いたコマンドは
#     誤って止まる。正しく解釈するにはシェルのパーサが要る。止まっても
#     理由は表示されるし、書き方を変えれば通るので、そこも見ない

set -uo pipefail

cmd=$(jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0
[ -n "$cmd" ] || exit 0

# --- ヒアドキュメントの本文を落とす ---------------------------------------
body=""
delim=""
while IFS= read -r line; do
    if [ -n "$delim" ]; then
        trimmed=${line#"${line%%[![:space:]]*}"}
        trimmed=${trimmed%"${trimmed##*[![:space:]]}"}
        [ "$trimmed" = "$delim" ] && delim=""
        continue
    fi
    body+="$line"$'\n'
    if [[ $line != *"<<<"* ]] &&
       [[ $line =~ \<\<-?[[:space:]]*[\'\"]?([A-Za-z_][A-Za-z0-9_]*) ]]; then
        delim=${BASH_REMATCH[1]}
    fi
done <<< "$cmd"

# 実データを指しているか。$HOME 起点の書き方だけを見る
touches_real_data() {
    case "$1" in
        *"~/ytsched/data"*)         return 0 ;;
        *'$HOME/ytsched/data'*)     return 0 ;;
        *'${HOME}/ytsched/data'*)   return 0 ;;
        *"$HOME/ytsched/data"*)     return 0 ;;
    esac
    return 1
}

# --- 区切りごとに先頭の語を見る -------------------------------------------
segments=$(printf '%s' "$body" | sed -e 's/&&/\n/g' -e 's/||/\n/g' -e 's/[;|&]/\n/g')

while IFS= read -r seg; do
    read -r -a words <<< "$seg" || true
    [ ${#words[@]} -gt 0 ] || continue

    i=0
    # 行頭の ( { ! と VAR=value、env / sudo / nice の前置きを飛ばす
    while [ $i -lt ${#words[@]} ]; do
        w=${words[$i]}
        w=${w#"${w%%[!\(\{!]*}"}
        words[$i]=$w
        case "$w" in
            ""|env|sudo|nice|nohup|time) i=$((i + 1)) ;;
            *=*)                         i=$((i + 1)) ;;
            *)                           break ;;
        esac
    done
    [ $i -lt ${#words[@]} ] || continue

    first=${words[$i]}
    rest=("${words[@]:$i}")

    # --- mise のタスク名を取り出す ----------------------------------------
    task=""
    if [ "$first" = "mise" ]; then
        j=1
        while [ $j -lt ${#rest[@]} ]; do
            case "${rest[$j]}" in
                -*) j=$((j + 1)) ;;
                run) j=$((j + 1)) ;;
                *)  task=${rest[$j]}; break ;;
            esac
        done
    fi

    # 1. 依存を上げ直すタスク（TODO-022）
    case "$task" in
        upgradeproject|uppj)
            printf 'mise run %s は依存を上げ直す（rm -f uv.lock → uv sync → uv pip install -U）。\n' "$task" >&2
            printf 'テストが壊れたとき、変更のせいか依存のせいか分からなくなる（TODO-022）。\n' >&2
            printf '走らせるのは利用者。fmt / typecheck / lint / test / build は叩いてよい。\n' >&2
            exit 2
            ;;
    esac

    # --- このセグメントのオプションを見る ---------------------------------
    has_datadir=""
    is_help=""
    for w in "${rest[@]}"; do
        case "$w" in
            --datadir|--datadir=*) has_datadir=yes ;;
            --help|-h|--version)   is_help=yes ;;
        esac
    done

    # 2. 実データを触るコマンド。読み取りだけのものは通す
    if touches_real_data "$seg"; then
        deny_reason=""

        # リダイレクト先が実データなら、先頭の語によらず書き込みになる。
        # `>` の右側の語を文字列として拾う。こうすると `1>` `2>` `&>` `>|`
        # `>>` や、空白の無い `x>>path` の書き方もまとめて拾える
        tail=$seg
        while [ "$tail" != "${tail#*>}" ]; do
            tail=${tail#*>}
            t=${tail#"${tail%%[![:space:]>|]*}"}
            t=${t%%[[:space:]]*}
            if touches_real_data "$t"; then
                deny_reason="リダイレクトで書き込もうとしている"
                break
            fi
        done

        if [ -z "$deny_reason" ]; then
            case "$first" in
                ls|cat|head|tail|less|more|grep|egrep|fgrep|rg|wc|stat|du|df|\
                diff|jq|file|echo|printf|test|\[|realpath|dirname|basename|\
                readlink|tree|sort|uniq|md5sum|sha256sum)
                    ;;
                git)
                    # コミットメッセージや検索語にパスを書くだけなら通す。
                    # 作業ファイルを書き換えるサブコマンドと -C だけ止める。
                    # -c のように値が次の語にあるフラグは、値ごと飛ばす
                    # （飛ばさないと値をサブコマンドと見て抜けてしまう）
                    j=1
                    while [ $j -lt ${#rest[@]} ]; do
                        w=${rest[$j]}
                        case "$w" in
                            -C|-C*|--work-tree|--work-tree=*)
                                deny_reason="git -C で実データを作業ツリーにしようとしている"
                                break
                                ;;
                            -c|--git-dir|--namespace|--exec-path)
                                j=$((j + 2))
                                ;;
                            -*)
                                j=$((j + 1))
                                ;;
                            rm|mv|clean|checkout|restore|reset|apply|stash|submodule)
                                deny_reason="git $w で書き換えようとしている"
                                break
                                ;;
                            *)
                                break
                                ;;
                        esac
                    done
                    ;;
                sed)
                    # sed -i は書き換える
                    for w in "${rest[@]}"; do
                        case "$w" in
                            -i|-i.*|--in-place|--in-place=*)
                                deny_reason="sed -i で書き換えようとしている"
                                ;;
                        esac
                    done
                    ;;
                find)
                    # find は探すだけなら通す
                    for w in "${rest[@]}"; do
                        case "$w" in
                            -delete|-exec|-execdir|-ok|-okdir)
                                deny_reason="find $w で書き換えようとしている"
                                ;;
                        esac
                    done
                    ;;
                *)
                    deny_reason="読み取り以外で触ろうとしている"
                    ;;
            esac
        fi

        if [ -n "$deny_reason" ]; then
            printf -- '%s/ytsched/data は実データ。%s。\n' "$HOME" "$deny_reason" >&2
            printf -- '起動を確かめるときは --datadir に一時ディレクトリを渡すこと。\n' >&2
            printf -- '中身が要るなら、一時ディレクトリへ複製してから試すこと。\n' >&2
            exit 2
        fi
        continue
    fi

    # 3. --datadir の無い ytsched の起動（既定の ~/ytsched/data を使ってしまう）
    [ -n "$has_datadir" ] && continue
    [ -n "$is_help" ] && continue

    starts_ytsched=""
    case "$first" in
        ytsched|uv|python|python3)
            for w in "${rest[@]:1}"; do
                [ "$w" = "ytsched" ] && starts_ytsched=yes && break
            done
            [ "$first" = "ytsched" ] && starts_ytsched=yes
            ;;
        mise)
            case "$task" in
                webapp|web|migrate) starts_ytsched=yes ;;
            esac
            ;;
    esac

    if [ -n "$starts_ytsched" ]; then
        printf -- '--datadir の無い ytsched の起動は、既定の %s/ytsched/data（実データ）を使う。\n' "$HOME" >&2
        printf -- '--datadir に一時ディレクトリを渡すこと。\n' >&2
        exit 2
    fi
done <<< "$segments"

exit 0
