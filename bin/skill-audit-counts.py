#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

import os
import sys

skills_dir = sys.argv[1] if len(sys.argv) > 1 else "skills"
results = []

for name in sorted(os.listdir(skills_dir)):
    skill_dir = os.path.join(skills_dir, name)
    if not os.path.isdir(skill_dir):
        continue
    skill_md = os.path.join(skill_dir, "SKILL.md")
    skill_lines = 0
    if os.path.exists(skill_md):
        with open(skill_md) as f:
            skill_lines = sum(1 for _ in f)
    ref_lines = 0
    script_lines = 0
    toolcall_lines = 0
    other_lines = 0

    for root, dirs, files in os.walk(skill_dir):
        for fn in files:
            fp = os.path.join(root, fn)
            if fn == "SKILL.md":
                continue
            try:
                with open(fp) as f:
                    lc = sum(1 for _ in f)
            except Exception:
                continue
            if "/references/" in fp:
                ref_lines += lc
            elif "/scripts/" in fp:
                script_lines += lc
            elif "/tool-calls/" in fp:
                toolcall_lines += lc
            else:
                other_lines += lc

    total = skill_lines + ref_lines + script_lines + toolcall_lines + other_lines
    results.append(
        (name, skill_lines, ref_lines, script_lines, toolcall_lines, other_lines, total)
    )

header = "skill|SKILL.md|references|scripts|tool-calls|other|total"
print(header)
print("|".join(["---"] * 7))
for r in results:
    print("|".join(str(x) for x in r))

print()
print(f"Total skills: {len(results)}")
print(f"Total SKILL.md lines: {sum(r[1] for r in results)}")
print(f"Total all lines: {sum(r[6] for r in results)}")

over_budget = [r for r in results if r[1] > 200]
print(f"\nOver SKILL.md budget (>200 lines): {len(over_budget)}")
for r in over_budget:
    print(f"  {r[0]}: {r[1]} lines ({r[1] - 200} over)")
