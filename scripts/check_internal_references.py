import os
import re

root_dir = os.path.abspath('.')
skip_dirs = {'.git', '.venv', 'node_modules', '.next', '__pycache__', '.ipynb_checkpoints', 'archive'}

targets = [
    'DecisionSphere-Complete-Project-Guide.md',
    'DecisionSphere-Assumptions-and-Limitations.md',
    'DecisionSphere-Glossary.md',
    'DecisionSphere-Number-Lineage.md',
    'Frontend-to-Research-Mapping.md',
    'DecisionSphere-Learning-Path.md',
    'DecisionSphere-Design-Rationale.md',
    'phase-3-supply-chain-plan-audit.md',
    'phase-4-workforce-audit.md',
    'phase-6-scenario-engine-audit.md',
    'phase-7-business-impact-audit.md',
    'phase-9-final-gate.md',
    'phase-9-foundation-and-architecture.md'
]

references = {t: [] for t in targets}

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in skip_dirs]
    for f in filenames:
        if not f.endswith(('.md', '.py', '.ts', '.tsx', '.json', '.tex')):
            continue
        filepath = os.path.join(dirpath, f)
        rel = os.path.relpath(filepath, root_dir).replace('\\', '/')
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                content = infile.read()
                for t in targets:
                    if t in content:
                        references[t].append(rel)
        except Exception as e:
            pass

print('=== INTERNAL REFERENCE AUDIT ===')
for t, refs in references.items():
    print(f'{t}: referenced in {len(refs)} files')
    for r in refs[:5]:
        print(f'   -> {r}')
