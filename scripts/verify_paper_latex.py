import os
import re
from collections import Counter

tex_path = "paper/DecisionSphere_Research_Paper.tex"
bib_path = "paper/references.bib"

with open(tex_path, "r", encoding="utf-8") as f:
    tex = f.read()

with open(bib_path, "r", encoding="utf-8") as f:
    bib = f.read()

# 1. BibTeX keys
bib_keys = set(re.findall(r"@\w+\s*{\s*([^,]+),", bib))
print(f"Total BibTeX keys found in {bib_path}: {len(bib_keys)}")
for k in sorted(bib_keys):
    print(f"  - {k}")

# 2. \cite{...} in tex
citations = set()
for c in re.findall(r"\\cite\{([^}]+)\}", tex):
    for key in c.split(","):
        citations.add(key.strip())

print(f"\nTotal citations found in {tex_path}: {len(citations)}")
missing_cites = citations - bib_keys
unused_bib = bib_keys - citations
print(f"Missing citations (in tex but not bib): {missing_cites}")
print(f"Unused BibTeX entries: {unused_bib}")

# 3. \includegraphics{...}
figures = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)
print(f"\nTotal figures included: {len(figures)}")
missing_figs = []
for fig in figures:
    fig_clean = fig.strip()
    if not os.path.exists(os.path.join("paper", fig_clean)) and not os.path.exists(fig_clean):
        missing_figs.append(fig_clean)
    else:
        print(f"  OK: {fig_clean}")
print(f"Missing figures on disk: {missing_figs}")

# 4. \ref{...} vs \label{...}
labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
refs = set(re.findall(r"\\ref\{([^}]+)\}", tex))
print(f"\nTotal labels: {len(labels)}")
print(f"Total refs: {len(refs)}")
missing_refs = refs - labels
print(f"Broken refs (referenced but no label): {missing_refs}")

# 5. Environment balance
begins = re.findall(r"\\begin\{([^}]+)\}", tex)
ends = re.findall(r"\\end\{([^}]+)\}", tex)
print(f"\nTotal \\begin: {len(begins)}, Total \\end: {len(ends)}")
if Counter(begins) != Counter(ends):
    print("WARNING: Environment mismatch!")
    from collections import Counter
    cb = Counter(begins)
    ce = Counter(ends)
    for env in set(begins) | set(ends):
        if cb[env] != ce[env]:
            print(f"  Mismatch in {env}: begin={cb[env]}, end={ce[env]}")
else:
    print("  OK: All LaTeX environments perfectly balanced.")

# 6. Tables audit
tables = re.findall(r"\\begin\{table\}", tex)
print(f"\nTotal table environments: {len(tables)}")
