"""
DecisionSphere — Automated Notebook Suite Executor
Executes all 16 notebooks in sequence, captures runtime metrics, and validates execution outputs.
"""
import os
import sys
import time
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

NOTEBOOKS_DIR = "notebooks"
NOTEBOOK_FILES = [
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

def execute_all():
    print(f"=== Starting Deterministic Execution of {len(NOTEBOOK_FILES)} Notebooks ===")
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    
    total_start = time.perf_counter()
    success_count = 0
    failures = []

    for nb_name in NOTEBOOK_FILES:
        nb_path = os.path.join(NOTEBOOKS_DIR, nb_name)
        if not os.path.exists(nb_path):
            print(f"  [MISSING] {nb_name} not found!")
            failures.append((nb_name, "File not found"))
            continue
            
        print(f"  [RUNNING] {nb_name}...", end="", flush=True)
        t0 = time.perf_counter()
        try:
            with open(nb_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
                
            # Execute with repository root as working directory
            ep.preprocess(nb, {"metadata": {"path": "."}})
            
            with open(nb_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
                
            elapsed = time.perf_counter() - t0
            print(f" DONE ({elapsed:.2f}s)")
            success_count += 1
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            print(f" FAILED ({elapsed:.2f}s): {exc}")
            failures.append((nb_name, str(exc)))

    total_time = time.perf_counter() - total_start
    print(f"\\n=== Notebook Suite Execution Summary ===")
    print(f"Total Time  : {total_time:.2f}s")
    print(f"Successful  : {success_count}/{len(NOTEBOOK_FILES)}")
    print(f"Failed      : {len(failures)}")
    if failures:
        print("Failures:")
        for name, err in failures:
            print(f"  - {name}: {err}")
        sys.exit(1)
    else:
        print("All notebooks executed successfully with 0 errors.")

if __name__ == "__main__":
    execute_all()
