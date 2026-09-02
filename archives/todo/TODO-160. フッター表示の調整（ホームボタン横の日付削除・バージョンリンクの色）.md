# TODO-160. フッター表示の調整（ホームボタン横の日付削除・バージョンリンクの色）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ |
| 実施 | Sonnet 5 / effort medium | main + verifier |

## きっかけ

フッターの見た目を 2 か所直したいという要望があった。

## やったこと

- `main.html` の `home_button` から、ホームアイコンの横にあった日付表示
  （`.my-home-date` の span、年・月日・曜日）を削除した。アイコンの
  クラスを `my-icon-home`（日付表示の高さに揃えたサイズ、TODO-102）から、
  他のフッターアイコンと同じ `my-icon-xl` に変更した。`my.css` から、
  使われなくなった `.my-home-date` と `.my-icon-home` の定義を削除した
- バージョン表示（`ytsched {{ version }}` を GitHub の User.md へ
  リンクしている箇所、TODO-158）について、`my.css` に
  `.my-version-info a { color: white; }` を足し、リンクの文字色を
  ブラウザ既定の青・訪問後の紫から常に白に固定した（下線は残した）

## テスト

verifier に依頼。

- `mise run lint` / `mise run test`（607 passed）: 通過
- `my-home-date` / `my-icon-home` の参照が、削除後はリポジトリ内に
  残っていないことを確認
- `--datadir` に一時ディレクトリを指定してアプリを起動し、
  `home_button` から日付テキストが消えていること、バージョン行の HTML が
  壊れていないこと、`my.css` に色の指定が正しく出力されていることを確認

`tools/screenshot.py` でキャプチャを撮り、チャットへ添付して見た目を
確認した（`imv -d` はこの端末では `DISPLAY` はあるものの X サーバーに
繋がらずクラッシュし、手元での表示はできなかった）。
