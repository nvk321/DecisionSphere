# DecisionSphere — Archive Directory & Historical Record

This directory preserves historical development documentation, phase audit reports, experimental notes, and exploratory artifacts generated during the iterative construction of DecisionSphere (Phases 1 through 11).

> [!NOTE]
> **Source of Truth Rule:**  
> Files in this directory represent point-in-time development milestones, exploratory audits, and historical working notes. For authoritative system documentation, refer strictly to the canonical files in `docs/`, `university_reviews/REVIEW_2/`, `paper/`, and the analytical core (`src/` and `models/`).

---

## Directory Organization

### 1. `archive/historical-audits/`
Point-in-time architectural audit reports and gate evaluations produced during development:
- `phase-3-supply-chain-plan-audit.md`: Historical audit of DataCo supply chain baseline classifier.
- `phase-4-workforce-audit.md`: Historical audit of IBM HR attrition modeling and class imbalance handling.
- `phase-6-scenario-engine-audit.md` & `phase-6-scenario-engine-post-audit.md`: Historical validation of scenario parameter mapping.
- `phase-7-business-impact-audit.md`: Architectural specification and pre-implementation audit for financial formulas.
- `phase-9-final-gate.md`: Quality gate validation for Phase 9 FastAPI backend integration.
- `phase-9-foundation-and-architecture.md`: Initial blueprint for backend API routes and Pydantic schemas.
- `pre-phase-9-research-and-architecture-audit.md`: Pre-backend architectural synthesis.
- `data-audit-report.md`: Exploratory data quality, missingness, and column profiling audit.
- `reference-project-audit.md`: Critical forensic audit of legacy reference projects and leakage bugs.
- `current-state.md`: Running development progress log up through Phase 10.
- `decision-log.md`: Chronological log of engineering decisions across all development sprints.
- `implementation-roadmap.md`: Early milestone roadmap.
- `implementation-quality-gates.md`: Milestone gating checklists.
- `assumptions-and-open-questions.md`: Early working list of modeling assumptions.

### 2. `archive/development-notes/`
Exploratory research documents, conceptual essays, and domain summaries:
- `anti-goals.md`: Project scope boundaries (superseded by `docs/project-guide.md`).
- `scope.md` & `problem-statement.md` & `project-overview.md`: Early drafts superseded by `docs/project-guide.md`.
- `literature-gap-matrix.md`: Preliminary literature review notes (incorporated into `paper/` and `docs/methodology.md`).
- `research-direction.md`, `research-contract.md`, `research-system-map.md`: Conceptual research framing.
- `ml-problem-definition.md` & `ml-evaluation-strategy.md`: Early modeling specifications (superseded by `docs/methodology.md`).
- `engineering-contract.md` & `experimental-design.md`: Development contracts.
- `data-contracts.md` & `data-pipeline.md`: Early data pipeline notes.
- `business-impact-analysis.md`: Early financial accounting scratch notes.
- `scenario-engine.md` & `recommendation-engine.md`: Early module functional designs.
- `frontend-requirements.md`, `frontend-research.md`, `frontend-architecture.md`: Pre-implementation frontend discovery notes.
- `DecisionSphere-Learning-Path.md`: Pedagogical reading guide (incorporated into `docs/project-guide.md`).
- `DecisionSphere-Design-Rationale.md`: Component architectural rationale (incorporated into `docs/architecture.md`).
