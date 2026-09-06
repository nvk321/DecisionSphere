"""
Normalizes all paths and root-anchoring in scripts/notebook_builders_part2.py and scripts/build_all_notebooks.py.
"""
import os

def normalize_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Normalize paths
    content = content.replace("../models/", "models/")
    content = content.replace("../data/", "data/")
    content = content.replace("../artifacts/", "artifacts/")
    content = content.replace("../reference/", "reference/")

    # 2. Add root-anchoring pattern
    target_pattern = """if ".." not in sys.path:
    sys.path.insert(0, "..")"""

    replacement_pattern = """# Ensure execution is anchored to project root
if not os.path.exists("src") and os.path.exists("../src"):
    os.chdir("..")
if "." not in sys.path:
    sys.path.insert(0, ".")"""

    content = content.replace(target_pattern, replacement_pattern)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Normalized {filepath}")

if __name__ == "__main__":
    normalize_file("scripts/notebook_builders_part2.py")
    normalize_file("scripts/build_all_notebooks.py")
    normalize_file("scripts/build_notebook_suite.py")
