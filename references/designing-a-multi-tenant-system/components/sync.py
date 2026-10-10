#!/usr/bin/env python3
"""Copies each component in this folder into every file that uses it.

A target marks the slot with a pair of comments:
    <!-- component:<name> start -->  ...  <!-- component:<name> end -->
Everything between the two lines is replaced by the component file.
Run this after you edit a component. Never edit a copy by hand.
"""
import io, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

TARGETS = [
    ROOT / "src/content/articles/designing-a-multi-tenant-system.md",
    ROOT / "references/designing-a-multi-tenant-system/presentation.html",
]

def main() -> int:
    changed = 0
    for target in TARGETS:
        text = io.open(target, encoding="utf-8").read()
        original = text
        for name in sorted(p.stem for p in HERE.glob("*.html")):
            body = io.open(HERE / f"{name}.html", encoding="utf-8").read().rstrip("\n")
            pattern = re.compile(
                r"(<!-- component:%s start -->\n)(?:.*?\n)??(<!-- component:%s end -->)"
                % (re.escape(name), re.escape(name)),
                re.S,
            )
            if not pattern.search(text):
                continue
            text = pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)
        if text != original:
            io.open(target, "w", encoding="utf-8").write(text)
            print(f"updated {target.relative_to(ROOT)}")
            changed += 1
        else:
            print(f"unchanged {target.relative_to(ROOT)}")
    return 0 if changed or True else 1

if __name__ == "__main__":
    sys.exit(main())
