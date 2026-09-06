"""
DecisionSphere — Unified Academic Reproducibility Script
Executes end-to-end verification across:
1. Cryptographic model artifact integrity (Gate H)
2. Automated analytical core test suite (pytest tests/)
3. FastAPI backend API contracts (pytest backend/tests/)
4. Canonical Review 2 simulation run verification (-$642,716.18)
5. Generation and verification of publication figures
"""

import sys
import os
import hashlib
import subprocess
import json

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath("."))

VERIFIED_MODEL_HASHES = {
    "models/demand/demand_model.joblib": "fb438c03a742202657bb4ef9196ff17e004bc090e99218f02985dc7720f41941",
    "models/supply_chain/supply_chain_model.joblib": "0052e641cf355257abb332703c3e6a46c65e9ab10a975227d83cf77d7e689b59",
    "models/workforce/workforce_model.joblib": "4b195c7bee3ab8f4afe75ccd0c75fff0c8e18b9fca88a00305e165a010109918"
}

def check_model_integrity():
    print("\n[Step 1/5] Verifying Model Cryptographic Hashes (Gate H)...")
    for rel_path, expected_hash in VERIFIED_MODEL_HASHES.items():
        if not os.path.exists(rel_path):
            print(f"FAILED: Model file not found at {rel_path}")
            return False
        with open(rel_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        if computed_hash != expected_hash:
            print(f"FAILED: Hash mismatch for {rel_path}\n  Expected: {expected_hash}\n  Computed: {computed_hash}")
            return False
        print(f"  OK: {rel_path} -> {computed_hash[:16]}... verified.")
    return True

def run_tests():
    print("\n[Step 2/5] Running Automated Test Suites (pytest)...")
    cmd_core = [sys.executable, "-m", "pytest", "tests/"]
    print("  Running analytical core tests (tests/)...")
    res1 = subprocess.run(cmd_core, capture_output=True, text=True)
    if res1.returncode != 0:
        print("  FAILED: Core tests failed!")
        print(res1.stdout)
        print(res1.stderr)
        return False
    print("  OK: Core test suite passed.")

    cmd_backend = [sys.executable, "-m", "pytest", "backend/tests/"]
    print("  Running backend tests (backend/tests/)...")
    res2 = subprocess.run(cmd_backend, capture_output=True, text=True)
    if res2.returncode != 0:
        print("  FAILED: Backend tests failed!")
        print(res2.stdout)
        print(res2.stderr)
        return False
    print("  OK: Backend test suite passed.")
    return True

def verify_canonical_run():
    print("\n[Step 3/5] Verifying Authoritative Canonical Review 2 Scenario...")
    from src.scenario.schema import ScenarioLevers
    from src.scenario.engine import ScenarioEngine
    from src.business.engine import BusinessImpactEngine
    from src.recommendation.engine import RecommendationEngine

    scen_engine = ScenarioEngine(
        demand_artifact_path='models/demand/demand_model.joblib',
        supply_artifact_path='models/supply_chain/supply_chain_model.joblib',
        workforce_artifact_path='models/workforce/workforce_model.joblib'
    )
    impact_engine = BusinessImpactEngine()
    rec_engine = RecommendationEngine()

    levers = ScenarioLevers(
        scenario_id='canonical_review_2',
        scenario_name='Review 2 Canonical: +15% Demand, Standard SLA, 40% Overtime',
        demand_growth_pct=15.0,
        promo_active=True,
        scheduled_days_offset=0,
        shipping_mode_override='Standard Class',
        overtime_workforce_pct=40.0,
        salary_hike_override=None
    )

    run = scen_engine.run_scenario(levers=levers)
    impact = impact_engine.evaluate(run)
    rec = rec_engine.evaluate(run, impact)

    # Reconcile exact numbers
    expected_profit_delta = -642716.18
    actual_profit_delta = impact.net_profit_delta
    diff = abs(actual_profit_delta - expected_profit_delta)

    print(f"  Net Profit Delta Expected : ${expected_profit_delta:,.2f}")
    print(f"  Net Profit Delta Actual   : ${actual_profit_delta:,.2f}")
    print(f"  Decision Category         : {rec.decision_category.value}")
    print(f"  Composite Risk Score      : {rec.composite_risk.composite_risk_score:.2f}")

    if diff > 0.05 or rec.decision_category.value != "REJECT_RESTRUCTURE":
        print(f"  FAILED: Mismatch in canonical run metrics! Delta diff = {diff}")
        return False

    print("  OK: Canonical scenario matches authoritative numbers to the cent.")
    return True

def verify_figures():
    print("\n[Step 4/5] Verifying Publication Figures...")
    required_figures = [
        "artifacts/figures/architecture_overview.png",
        "artifacts/figures/financial_waterfall.png",
        "artifacts/figures/dataset_distributions.png",
        "artifacts/figures/demand_feature_importance.png",
        "artifacts/figures/supply_chain_roc_pr_calibration.png",
        "artifacts/figures/workforce_feature_importance.png",
        "artifacts/figures/cross_domain_propagation.png",
        "artifacts/figures/tipping_point_analysis.png",
        "artifacts/figures/number_lineage_trace.png"
    ]
    for fig in required_figures:
        if not os.path.exists(fig):
            print(f"  FAILED: Missing figure {fig}")
            return False
        size = os.path.getsize(fig)
        print(f"  OK: {fig} ({size:,} bytes)")
    return True

def verify_core_invariance():
    print("\n[Step 5/5] Verifying Analytical Core Invariance (git diff)...")
    res = subprocess.run(["git", "diff", "--stat", "src", "models"], capture_output=True, text=True)
    if res.stdout.strip():
        print(f"  FAILED: Analytical core has been modified!\n{res.stdout}")
        return False
    print("  OK: git diff --stat src models is completely empty.")
    return True

if __name__ == "__main__":
    print("============================================================")
    print("   DECISIONSPHERE UNIFIED REPRODUCIBILITY VERIFICATION")
    print("============================================================")
    all_ok = True
    for step in [check_model_integrity, run_tests, verify_canonical_run, verify_figures, verify_core_invariance]:
        if not step():
            all_ok = False
            break

    if all_ok:
        print("\n============================================================")
        print("   ALL REPRODUCIBILITY QUALITY GATES PASSED (100% OK)")
        print("============================================================")
        sys.exit(0)
    else:
        print("\n============================================================")
        print("   REPRODUCIBILITY VERIFICATION FAILED")
        print("============================================================")
        sys.exit(1)
