import sys
import os
sys.path.insert(0, os.path.abspath("."))
import time
import tracemalloc

import numpy as np
import pandas as pd

from src.scenario.state import ScenarioStateVector
from src.scenario.graph import ScenarioDependencyGraph
from src.scenario.propagation import StatePropagationOperator
from src.scenario.schema import ScenarioLevers

def main():
    print("=== DECISIONSPHERE INDEPENDENT CLAIM VERIFICATION ===")
    
    # Claim 2: 24-dimensional state vector
    dim = ScenarioStateVector.state_dimension()
    feat_names = ScenarioStateVector.feature_names()
    print(f"Claim 2: State vector dimension = {dim} (len feature_names = {len(feat_names)})")
    
    # Claim 3: 11-node / 18-edge dependency graph
    g = ScenarioDependencyGraph()
    num_nodes = len(g.nodes)
    num_edges = len(g.edges)
    is_dag = g.is_acyclic()
    top_order = g.topological_sort()
    print(f"Claim 3: Graph nodes = {num_nodes}, edges = {num_edges}, is_dag = {is_dag}, top_order len = {len(top_order)}")

    
    # Operator initialization
    tracemalloc.start()
    t0 = time.perf_counter()
    op = StatePropagationOperator()
    t_init = time.perf_counter() - t0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Operator init time: {t_init:.4f}s, Peak memory: {peak_mem / 1024:.2f} KB")
    
    # Canonical Scenario Levers
    levers = ScenarioLevers(
        scenario_name="CanonicalVerification",
        promo_active=True,
        demand_growth_pct=15.0,
        scheduled_days_offset=0,
        shipping_mode_override="Standard Class",
        overtime_workforce_pct=40.0,
    )
    
    # Claim 9: Execution latency & memory
    tracemalloc.start()
    t0 = time.perf_counter()
    st, run, imp, rec = op.evaluate_state(levers)
    t_eval = time.perf_counter() - t0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Claim 9: Single scenario execution latency = {t_eval*1000:.2f} ms, Peak memory = {peak_mem / 1024:.2f} KB")
    
    # Claim 6: Financial Impact
    net_profit_delta = float(imp.net_profit_delta)
    crs = float(rec.composite_risk.composite_risk_score)
    decision = rec.decision_category.value
    print(f"Claim 6: Net Profit Delta = ${net_profit_delta:,.2f}, CRS = {crs:.2f}, Decision = {decision}")
    
    # Claim 4: Jacobian Computation
    t0 = time.perf_counter()
    J, row_names, col_names = op.compute_sensitivity_jacobian(levers, epsilon=1.0)
    t_jac = time.perf_counter() - t0
    print(f"Claim 4: Jacobian shape = {J.shape}, rows = {len(row_names)}, cols = {len(col_names)}, time = {t_jac*1000:.2f} ms")
    print(f"   J[0] (demand sales vs demand_growth): {J[0, 0]:.4f}")
    print(f"   J[4] (late prob vs demand_growth): {J[4, 0]:.6f}")
    print(f"   J[8] (attrition prob vs overtime): {J[8, 2]:.6f}")
    
    # Claim 5: Tipping point investigation
    print("\n--- Investigating Claim 5: Tipping Point ---")
    tp_default = op.find_margin_tipping_point(levers)
    print(f"Default levers (overtime=40.0) tipping point search: {tp_default}")
    
    # What if overtime is 0%?
    levers_no_ot = levers.model_copy(update={"overtime_workforce_pct": 0.0})
    tp_no_ot = op.find_margin_tipping_point(levers_no_ot)
    print(f"Zero overtime (overtime=0.0) tipping point search: {tp_no_ot}")
    
    # What if no promo and no overtime?
    levers_clean = levers.model_copy(update={"promo_active": False, "overtime_workforce_pct": 0.0})
    tp_clean = op.find_margin_tipping_point(levers_clean)
    print(f"No promo & zero overtime tipping point search: {tp_clean}")

    # Let's inspect the tipping_point.csv from EXP-005
    tp_csv_path = "research/experiments/EXP-005-sensitivity-tipping-points/results/tipping_point.csv"
    if os.path.exists(tp_csv_path):
        df_tp = pd.read_csv(tp_csv_path)
        print(f"EXP-005 tipping_point.csv shape: {df_tp.shape}")
        print("First 3 rows:")
        print(df_tp[["Demand_Shock_Pct", "Delta_Realized_Revenue", "Delta_Logistics_Cost", "Delta_Workforce_Cost", "Net_Profit_Delta"]].head(3))
        # Where does profit cross zero?
        pos = df_tp[df_tp["Net_Profit_Delta"] > 0]
        neg = df_tp[df_tp["Net_Profit_Delta"] < 0]
        print(f"Number of rows with Net_Profit_Delta > 0: {len(pos)}, < 0: {len(neg)}")
    
    # Claim 7: ECE reduction
    calib_csv = "research/experiments/EXP-002-probability-calibration/results/calibration_metrics.csv"
    if os.path.exists(calib_csv):
        df_cal = pd.read_csv(calib_csv)
        sc_raw = df_cal[(df_cal["Domain"] == "Supply Chain") & (df_cal["Metric"] == "Raw ECE")]["Value"].values[0]
        sc_cal = df_cal[(df_cal["Domain"] == "Supply Chain") & (df_cal["Metric"] == "Calibrated ECE")]["Value"].values[0]
        ece_drop = (sc_raw - sc_cal) / sc_raw * 100.0
        print(f"\nClaim 7: Supply Chain Raw ECE = {sc_raw}, Calibrated ECE = {sc_cal}, Reduction = {ece_drop:.2f}%")

    # Claim 8: Decision Stability (Monte Carlo N=50)
    print("\n--- Investigating Claim 8: Decision Stability (Monte Carlo) ---")
    np.random.seed(42)
    decisions = []
    profits = []
    for _ in range(50):
        noisy_demand = float(np.clip(np.random.normal(15.0, 3.0), 0.0, 30.0))
        noisy_ot = float(np.clip(np.random.normal(40.0, 5.0), 0.0, 100.0))
        l_noise = levers.model_copy(update={"demand_growth_pct": noisy_demand, "overtime_workforce_pct": noisy_ot})
        _, _, imp_noise, rec_noise = op.evaluate_state(l_noise)
        decisions.append(rec_noise.decision_category.value)
        profits.append(float(imp_noise.net_profit_delta))
    stability = (decisions.count("REJECT_RESTRUCTURE") / len(decisions)) * 100.0
    print(f"Claim 8: Monte Carlo N=50 stability = {stability:.1f}%, mean profit delta = ${np.mean(profits):,.2f}, 95% CI = [${np.percentile(profits, 2.5):,.2f}, ${np.percentile(profits, 97.5):,.2f}]")

if __name__ == "__main__":
    main()
