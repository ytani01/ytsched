# TODO-155. cron の設定例を User.md に書く

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort low | main のみ |
| 実施 | Sonnet 5 / effort low | main のみ |

## きっかけ

TODO-153 のアーカイブに書いた cron の例が、利用者向け文書のどこにも
出ていなかった。

## やったこと

`docs/User.md` の「12. 毎朝の通知」に、TODO-153 のアーカイブにある
cron の例をそのまま追記した。

```
0 7 * * * $HOME/.local/bin/ytsched notify | $HOME/bin/slack-send.sh -c '#ytsched' -t 'ytsched'
```

## テスト

文書の追記のみのため、実行して確かめるものは無い。
