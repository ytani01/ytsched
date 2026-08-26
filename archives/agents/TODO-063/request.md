# TODO-063 の依頼

## 変更の内容

`src/ytsched/webroot/static/js/my.js` の `moveToMonday()` だけを直した。

変更前:

```javascript
    let days;
    if ( direction > 0 ) {
        days = 8 - wday;
    } else {
        days = 1 - wday;
        if (days == 0) {
            days = -7; // Mon
        }
    }
```

変更後:

```javascript
    const days = (1 - wday) + (direction > 0 ? 7 : -7);
```

（`wday` は日曜を 7 に直したあとの 1..7）

## 背景

ホームボタンは `date=今日` を渡すので、今日が週の途中（例: 水曜）だと
`cur_day` が水曜になる。変更前は前へ送るときに「同じ週の月曜」になり、
週が送れなかった。まず `cur_day` をその週の月曜に丸めてから前後へ 7 日
ずらす形にした。

サーバー側は渡された日付から月曜を計算して週を出しているので、表示されて
いる週自体は正しい。ずれていたのは `cur_day` から次に要求する日付だけ。

詳しくは `TODO.md` の TODO-063 の節を読むこと。
