import os
import json

root_dir = os.path.abspath('.')
inventory = []
skip_dirs = {'.git', '.venv', 'node_modules', '.next', '__pycache__', '.ipynb_checkpoints'}

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in skip_dirs]
    for f in filenames:
        rel = os.path.relpath(os.path.join(dirpath, f), root_dir).replace('\\', '/')
        size = os.path.getsize(os.path.join(dirpath, f))
        inventory.append({'path': rel, 'size': size})

categories = {
    'runtime_critical': [],
    'research_critical': [],
    'review2_critical': [],
    'paper_critical': [],
    'generated_artifact': [],
    'historical_development': [],
    'duplicate_redundant': [],
    'obsolete': []
}

for item in inventory:
    p = item['path']
    if p.startswith('.pytest_cache/') or p.startswith('.coverage') or p in ['inventory_raw.json', 'inventory_classified.json']:
        categories['obsolete'].append(p)
        continue

    # Analytical core and models
    if p.startswith('src/') or p.startswith('models/'):
        categories['research_critical'].append(p)
    elif p.startswith('backend/') or p.startswith('frontend/'):
        categories['runtime_critical'].append(p)
    elif p.startswith('data/'):
        categories['research_critical'].append(p)
    elif p.startswith('tests/'):
        categories['research_critical'].append(p)
    elif p.startswith('notebooks/'):
        categories['research_critical'].append(p)
    elif p.startswith('artifacts/'):
        categories['generated_artifact'].append(p)
    elif p.startswith('reference/'):
        categories['historical_development'].append(p)
    elif p.startswith('university_reviews/'):
        categories['review2_critical'].append(p)
    elif p.startswith('docs/research-paper-materials/'):
        categories['paper_critical'].append(p)
    elif p.startswith('docs/architecture-decisions/'):
        categories['research_critical'].append(p)
    elif p.startswith('docs/phase-') or p.startswith('docs/pre-phase-'):
        categories['historical_development'].append(p)
    elif p in [
        'docs/reference-project-audit.md', 'docs/anti-goals.md', 'docs/literature-gap-matrix.md',
        'docs/research-direction.md', 'docs/research-contract.md', 'docs/scope.md',
        'docs/problem-statement.md', 'docs/project-overview.md', 'docs/data-contracts.md',
        'docs/data-pipeline.md', 'docs/decision-log.md', 'docs/engineering-contract.md',
        'docs/experimental-design.md', 'docs/implementation-quality-gates.md',
        'docs/implementation-roadmap.md', 'docs/ml-evaluation-strategy.md',
        'docs/ml-problem-definition.md', 'docs/research-system-map.md', 'docs/xai-strategy.md',
        'docs/current-state.md', 'docs/data-audit-report.md'
    ]:
        categories['historical_development'].append(p)
    elif p in [
        'docs/DecisionSphere-Assumptions-and-Limitations.md',
        'docs/DecisionSphere-Complete-Project-Guide.md',
        'docs/DecisionSphere-Design-Rationale.md',
        'docs/DecisionSphere-Glossary.md',
        'docs/DecisionSphere-Learning-Path.md',
        'docs/DecisionSphere-Number-Lineage.md',
        'docs/Frontend-to-Research-Mapping.md'
    ]:
        categories['duplicate_redundant'].append(p)
    elif p.startswith('docs/frontend-'):
        categories['runtime_critical'].append(p)
    elif p.startswith('docs/'):
        categories['research_critical'].append(p)
    elif p.startswith('scripts/'):
        categories['research_critical'].append(p)
    elif p in ['Dockerfile', 'docker-compose.yml', 'docker-entrypoint.sh', '.dockerignore', '.env.example', 'alembic.ini', 'requirements.txt', 'package.json']:
        categories['runtime_critical'].append(p)
    elif p in ['README.md', 'AGENTS.md', 'LICENSE', 'CITATION.cff', '.gitignore']:
        categories['research_critical'].append(p)
    else:
        categories['historical_development'].append(p)

print('=== TOTAL REPOSITORY FILES ===', len(inventory))
for cat, items in categories.items():
    print(f'{cat}: {len(items)} files')

with open('inventory_classified.json', 'w') as out:
    json.dump(categories, out, indent=2)
