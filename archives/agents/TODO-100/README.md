# TODO-100 の分担

`src` と `tests` の 9 ファイルにまたがり、外から見える属性の型が変わる
（`str` → `Path`）ので、実装を implementer に分けた。

| 担当 | 見たところ | 報告 |
|------|-----------|------|
| main | 属性の型を変えるか、呼び出し側で包むだけにするかを利用者と決めた。docstring の ``os.stat()`` 表記を揃えた | — |
| implementer | 書き換えと `extend-select` への `PTH` 追加 | [implementer-report.md](implementer-report.md)（[依頼](implementer-request.md)） |
| verifier | 新旧でパスと `.bak` の名前が一致するか、`~` の展開、CLI から `str` を渡す経路、lint・型チェック・テスト | [verifier-report.md](verifier-report.md)（[依頼](verifier-request.md)） |
| wording | コミットに入る `.md` の、前例の無い語 | [wording-report.md](wording-report.md) |

`reviewer` は入れていない。挙動を変えない書き換えで、分岐も増えないため。
挙動が変わっていないことの確認は verifier に、**新旧の実装を実際に呼び
比べる**形で見させた。

`expanduser()` の差を対応しないと決めた理由は
[TODO-100 の archives](../../todo/TODO-100.%20os.path%20を%20pathlib%20へ移す.md)
に書いた。
