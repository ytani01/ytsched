#!/usr/bin/env python3
"""TODO-175 でやった集計を再現するスクリプト。

`docs/token-usage-analysis.md` の数字は、これを走らせて出したもの
（一部は `tools/token-usage.py` の `collect()` / `total_of()` /
`sum_by()` を直に呼んでいる。そちらは transcript 全体の集計用）。

実行にはリポジトリのルートで ``uv run python
archives/agents/TODO-175/measure.py`` とする。

## 気をつけたこと（TODO-175 の verifier が見つけたもの）

``git show --numstat`` は、ファイル名に非 ASCII 文字（日本語のタイトルを
含む ``archives/todo/*.md`` など）が入っていると、その行を
``"archives/todo/TODO-063. ...\\343..."`` のように **二重引用符と
バックスラッシュエスケープ**で返す。素朴に ``path.startswith("archives/")``
で除くと、この行はすり抜けて **アーカイブ済みファイル自身の行数が
本文の変更に紛れ込む**（TODO-063 は 13 行のはずが 90 行と誤集計されて
いた）。``--numstat`` は素通しにできないので、この非引用化ができる
``git log`` の他のオプションは無い。ここでは ``-z``
（NUL 区切り、ファイル名をクォートしない）を使って避けている。
"""

import re
import statistics as st
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ARCHIVES_TODO = REPO / "archives" / "todo"


def parse_archives() -> list[dict]:
    """`archives/todo/*.md` から見込み・実施・消費・割合の行を拾う。"""
    rows = []
    for f in sorted(ARCHIVES_TODO.glob("*.md")):
        m = re.match(r"TODO-(\d+)\.\s*(.*)\.md$", f.name)
        if not m:
            continue
        num, title = int(m.group(1)), m.group(2)
        txt = f.read_text(encoding="utf-8")
        row = {"num": num, "title": title}

        for key, label in (("mikomi", "見込み"), ("jisshi", "実施")):
            mm = re.search(
                r"^[|\-\s*]*" + label + r"[|:：\s]*(.+)$", txt, re.MULTILINE
            )
            row[key] = mm.group(1).strip().rstrip("|").strip() if mm else ""

        mm = re.search(
            r"output\s*([\d,]+)\s*/\s*cache_creation\s*([\d,]+)", txt
        )
        row["output"] = int(mm.group(1).replace(",", "")) if mm else None
        row["cc"] = int(mm.group(2).replace(",", "")) if mm else None

        mm = re.search(r"概算\s*\$([\d,.]+)", txt)
        row["cost"] = float(mm.group(1).replace(",", "")) if mm else None

        mm = re.search(
            r"^\s*\|?\s*\|\s*"
            r"((?:main|implementer|verifier|reviewer|wording|writer|runner)"
            r"[^|]*?)（料金の割合）",
            txt,
            re.MULTILINE,
        )
        row["share"] = mm.group(1).strip() if mm else ""
        rows.append(row)
    return rows


def parse_share(s: str) -> dict[str, int]:
    return {
        m.group(1): int(m.group(2))
        for m in re.finditer(
            r"(main|implementer|verifier|reviewer|wording|writer|runner)"
            r"\s*(?:×\d+\s*)?(\d+)%",
            s,
        )
    }


def diff_lines() -> dict[int, tuple[int, ...]]:
    """TODO 番号ごとに `(追加行, 削除行, ファイル数)` を集める。

    `archives/` と `TODO.md` は除く。**`-z` でファイル名の
    クォートを避ける**（このモジュールの docstring を参照）。
    """
    log = subprocess.run(
        ["git", "log", "--pretty=format:%H\x1f%s", "--all"],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    ).stdout
    pairs = []
    for line in log.split("\n"):
        h, _, s = line.partition("\x1f")
        m = re.search(r"TODO-(\d+)", s)
        if m and not s.startswith("docs(todo):"):
            pairs.append((int(m.group(1)), h))

    result: dict[int, list[int]] = {}
    for num, commit in pairs:
        out = subprocess.run(
            ["git", "show", "--numstat", "-z", "--format=", "-M", commit],
            capture_output=True,
            text=True,
            cwd=REPO,
            check=False,
        ).stdout
        parts = out.split("\x00")
        add = dele = files = 0
        i = 0
        while i < len(parts):
            entry = parts[i]
            if not entry.strip():
                i += 1
                continue
            cols = entry.split("\t")
            if len(cols) == 3 and (cols[0].isdigit() or cols[0] == "-"):
                a, d, path = cols
                if path == "":
                    # リネーム: 続く 2 要素が旧パス・新パス
                    path = parts[i + 2]
                    i += 3
                else:
                    i += 1
                if path.startswith("archives/") or path == "TODO.md":
                    continue
                if a.isdigit() and d.isdigit():
                    add += int(a)
                    dele += int(d)
                    files += 1
            else:
                i += 1
        entry = result.setdefault(num, [0, 0, 0])
        entry[0] += add
        entry[1] += dele
        entry[2] += files
    return {k: tuple(v) for k, v in result.items()}


def agents_match(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """見込みと実施の担当の顔ぶれ（main を除く）が一致するかで分ける。"""

    def ags(s: str) -> frozenset[str]:
        return frozenset(
            re.findall(
                r"(implementer|verifier|reviewer|wording|writer|runner)", s
            )
        )

    c = [r for r in rows if r["cost"]]
    same = [r for r in c if ags(r["mikomi"]) == ags(r["jisshi"])]
    diff = [r for r in c if ags(r["mikomi"]) != ags(r["jisshi"])]
    return same, diff


def main() -> None:
    rows = parse_archives()
    lines = diff_lines()
    for r in rows:
        d = lines.get(r["num"])
        r["lines"] = (d[0] + d[1]) if d else 0
        r["sh"] = parse_share(r["share"])

    costed = [r for r in rows if r["cost"]]
    print(f"消費の記録がある項目: {len(costed)} 件")
    print(
        f"合計 ${sum(r['cost'] for r in costed):.1f}"
        f"  平均 ${sum(r['cost'] for r in costed) / len(costed):.2f}"
        f"  中央値 ${st.median([r['cost'] for r in costed]):.2f}"
    )

    print("\n=== 変更量でならす（30 行以上） ===")
    sized = [r for r in costed if r["lines"] >= 30 and r["sh"]]

    def rep(sel: list[dict], label: str) -> None:
        if not sel:
            print(f"  {label}: n=0")
            return
        per100 = [r["cost"] / r["lines"] * 100 for r in sel]
        print(
            f"  {label:20} n={len(sel):3}"
            f"  100 行あたり中央 ${st.median(per100):.2f}"
        )

    rep(
        [r for r in sized if r["sh"].get("implementer", 0) > 0],
        "implementer あり",
    )
    rep(
        [r for r in sized if r["sh"].get("implementer", 0) == 0],
        "main が実装",
    )
    rep([r for r in sized if r["sh"].get("main", 0) >= 85], "main 85%以上")

    print("\n=== 見込み・実施の担当が一致したか ===")
    same, diff = agents_match(rows)
    print(
        f"  一致 n={len(same)} 中央値 ${st.median([r['cost'] for r in same]):.2f}"
    )
    print(
        f"  不一致 n={len(diff)} 中央値 ${st.median([r['cost'] for r in diff]):.2f}"
    )

    print("\n=== 番号帯ごと ===")
    for lo in range(40, 180, 20):
        band = [r for r in costed if lo <= r["num"] < lo + 20]
        band_lines = [r for r in band if r["lines"]]
        per100 = (
            st.median([r["cost"] / r["lines"] * 100 for r in band_lines])
            if band_lines
            else None
        )
        per100_disp = f"${per100:.2f}" if per100 else "-"
        print(
            f"  TODO-{lo:03d}〜{lo + 19:03d} n={len(band):3}"
            f"  料金中央 ${st.median([r['cost'] for r in band]):.2f}"
            f"  100行あたり中央 {per100_disp}"
        )

    for num in (63, 59, 77, 69, 47, 49, 48):
        r = next(x for x in rows if x["num"] == num)
        print(f"TODO-{num:03d}: lines={r['lines']} cost={r['cost']}")


if __name__ == "__main__":
    main()
