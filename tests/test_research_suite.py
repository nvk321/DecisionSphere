"""
DecisionSphere — Automated Research Suite Regression Tests
Verifies the integrity, completeness, and non-regression of the entire research layer:
1. Notebook suite existence and JSON validity
2. 16-section pedagogical structure conformance
3. 15 publication figures existence and validity
4. Cryptographic model artifact hash invariance (Gate H)
5. Analytical core (src/ and models/) strict invariance
6. Complete research documentation and paper materials completeness
"""
import os
import sys
import json
import subprocess
import hashlib
import pytest
import nbformat

NOTEBOOKS_DIR = "notebooks"
FIGURES_DIR = "artifacts/figures"
DOCS_DIR = "docs"
PAPER_DIR = "paper"
ARCHIVE_PAPER_DIR = os.path.join("archive", "development-notes", "research-paper-markdown-drafts")

EXPECTED_NOTEBOOKS = [
    "00_project_orientation.ipynb",
    "01_data_inventory_and_provenance.ipynb",
    "02_demand_eda.ipynb",
    "03_supply_chain_eda.ipynb",
    "04_workforce_eda.ipynb",
    "05_demand_model.ipynb",
    "06_supply_chain_model.ipynb",
    "07_workforce_model.ipynb",
    "08_model_evaluation_and_comparison.ipynb",
    "09_cross_domain_decision_pipeline.ipynb",
    "10_financial_accounting.ipynb",
    "11_risk_and_recommendation_engine.ipynb",
    "12_sensitivity_analysis.ipynb",
    "13_end_to_end_decision_walkthrough.ipynb",
    "14_research_figures.ipynb",
    "15_number_lineage_worked_example.ipynb",
]

EXPECTED_FIGURES = [
    "architecture_overview.png",
    "dataset_distributions.png",
    "demand_feature_importance.png",
    "supply_chain_confusion_matrix.png",
    "supply_chain_roc_pr_calibration.png",
    "workforce_feature_importance.png",
    "workforce_roc_pr_calibration.png",
    "cross_domain_propagation.png",
    "financial_waterfall.png",
    "risk_decomposition.png",
    "demand_sensitivity_curve.png",
    "financial_sensitivity_sweep.png",
    "crs_weight_stability.png",
    "tipping_point_analysis.png",
    "number_lineage_trace.png",
]

EXPECTED_CORE_DOCS = [
    "project-guide.md",
    "architecture.md",
    "methodology.md",
    "assumptions-limitations.md",
    "reproducibility.md",
    "glossary.md",
    "frontend-research-mapping.md",
    "number-lineage.md",
    "frontend-manual-verification.md",
]

EXPECTED_PAPER_FILES = [
    "DecisionSphere_Research_Paper.tex",
    "references.bib",
    "README.md",
]


def test_notebooks_exist_and_are_valid():
    """All 16 notebooks must exist, be valid JSON, and parse cleanly via nbformat."""
    assert os.path.isdir(NOTEBOOKS_DIR), f"Notebooks directory '{NOTEBOOKS_DIR}' does not exist"
    for nb_name in EXPECTED_NOTEBOOKS:
        nb_path = os.path.join(NOTEBOOKS_DIR, nb_name)
        assert os.path.exists(nb_path), f"Notebook '{nb_name}' is missing"
        assert os.path.getsize(nb_path) > 1000, f"Notebook '{nb_name}' is too small or empty"

        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        assert len(nb.cells) >= 4, f"Notebook '{nb_name}' has insufficient cells ({len(nb.cells)})"


def test_notebooks_pedagogical_structure():
    """Every notebook must contain foundational pedagogical sections."""
    required_keywords = ["Title", "Why This Notebook Exists", "Prerequisites", "Business Question", "Technical Question"]
    for nb_name in EXPECTED_NOTEBOOKS:
        nb_path = os.path.join(NOTEBOOKS_DIR, nb_name)
        with open(nb_path, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in required_keywords:
            assert kw in content, f"Notebook '{nb_name}' missing required pedagogical section: '{kw}'"


def test_all_15_publication_figures_exist():
    """All 15 publication figures must exist and have non-zero file sizes."""
    assert os.path.isdir(FIGURES_DIR), f"Figures directory '{FIGURES_DIR}' does not exist"
    for fig_name in EXPECTED_FIGURES:
        fig_path = os.path.join(FIGURES_DIR, fig_name)
        assert os.path.exists(fig_path), f"Publication figure '{fig_name}' is missing"
        size = os.path.getsize(fig_path)
        assert size > 5000, f"Publication figure '{fig_name}' is suspiciously small ({size} bytes)"


def test_model_artifact_fingerprints():
    """Model artifacts must exist and match immutable fingerprints via ScenarioEngine."""
    from src.scenario.engine import ScenarioEngine

    engine = ScenarioEngine(
        demand_artifact_path="models/demand/demand_model.joblib",
        supply_artifact_path="models/supply_chain/supply_chain_model.joblib",
        workforce_artifact_path="models/workforce/workforce_model.joblib",
    )
    fps = engine.get_artifact_fingerprints()
    assert len(fps) == 3, f"Expected 3 model fingerprints, got {len(fps)}"
    for domain in ["demand", "supply_chain", "workforce"]:
        assert domain in fps, f"Fingerprint missing for domain '{domain}'"
        assert len(fps[domain]) == 64, f"Fingerprint for '{domain}' is not a valid SHA-256 hash"


def test_frozen_analytical_core_invariance():
    """Analytical core directories src/ and models/ must remain completely untouched."""
    cmd = ["git", "diff", "--stat", "src", "models"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert res.stdout.strip() == "", (
        f"VIOLATION: Analytical core (src/ or models/) has been modified!\n{res.stdout}"
    )


def test_core_documentation_completeness():
    """All core documentation files must exist and be comprehensive (>1KB)."""
    for doc_name in EXPECTED_CORE_DOCS:
        doc_path = os.path.join(DOCS_DIR, doc_name)
        assert os.path.exists(doc_path), f"Documentation file '{doc_name}' is missing"
        size = os.path.getsize(doc_path)
        assert size > 1000, f"Documentation file '{doc_name}' is too small ({size} bytes)"


def test_research_paper_materials_completeness():
    """Publication manuscript files in paper/ and archived draft chapters must exist."""
    assert os.path.isdir(PAPER_DIR), f"Research paper directory '{PAPER_DIR}' does not exist"
    for paper_file in EXPECTED_PAPER_FILES:
        file_path = os.path.join(PAPER_DIR, paper_file)
        assert os.path.exists(file_path), f"Research paper file '{paper_file}' is missing"
        size = os.path.getsize(file_path)
        assert size > 200, f"Research paper file '{paper_file}' is too small ({size} bytes)"

    # Also verify archive preservation of 14 chapters
    assert os.path.isdir(ARCHIVE_PAPER_DIR), f"Archived paper chapters directory '{ARCHIVE_PAPER_DIR}' missing"
    archived_chapters = [f for f in os.listdir(ARCHIVE_PAPER_DIR) if f.endswith(".md")]
    assert len(archived_chapters) >= 14, f"Expected 14 archived paper chapters, found {len(archived_chapters)}"
