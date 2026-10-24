"""
DecisionSphere — Automated Regression Tests for Patent Core Modules
Verifies formal state-space vector representation, dependency graph DAG validity,
topological sorting, and propagation operator monotonicity.
"""

import pytest
import numpy as np

from src.scenario.schema import ScenarioLevers, ScenarioAssumptions
from src.scenario.state import ScenarioStateVector
from src.scenario.graph import ScenarioDependencyGraph
from src.scenario.propagation import StatePropagationOperator


def test_state_vector_dimension_and_serialization():
    """Verifies that ScenarioStateVector has dimension k=24 and serializes correctly to NumPy."""
    assert ScenarioStateVector.state_dimension() == 24
    assert len(ScenarioStateVector.feature_names()) == 24

    st = ScenarioStateVector(
        sales_baseline=1000.0,
        sales_scenario=1150.0,
        sales_delta=150.0,
        daily_sales_rate=82.14,
        cycle_volume=2464.28,
        order_volume=2464.28,
        late_prob_baseline=0.55,
        late_prob_scenario=0.62,
        late_prob_delta=0.07,
        scheduled_days_offset=0.0,
        expedited_shipping_flag=0.0,
        attrition_prob_baseline=0.16,
        attrition_prob_scenario=0.19,
        attrition_prob_delta=0.03,
        overtime_percentage=40.0,
        work_life_balance_decrement=-1.0,
        gross_revenue_delta=1500.0,
        realized_revenue_delta=1350.0,
        supply_chain_cost_delta=4000.0,
        workforce_cost_delta=2000.0,
        net_profit_delta=-4650.0,
        supply_risk_index=65.0,
        workforce_risk_index=45.0,
        composite_risk_score=55.0,
    )

    arr = st.to_numpy()
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (24,)
    assert arr.dtype == np.float64
    assert st.state_norm() > 0.0

    st_perturbed = st.model_copy(update={"sales_scenario": 1200.0})
    dist = st.distance_to(st_perturbed)
    assert dist > 0.0
    assert np.isclose(dist, 50.0)


def test_dependency_graph_dag_and_topological_sort():
    """Verifies that the state-space dependency graph G=(V,E) is a valid acyclic DAG."""
    graph = ScenarioDependencyGraph()

    assert len(graph.nodes) == 11
    assert len(graph.edges) >= 15
    assert graph.is_acyclic() is True

    topo_order = graph.topological_sort()
    assert len(topo_order) == 11
    assert topo_order[0] == "N1_SCENARIO_LEVERS"
    assert topo_order[-1] == "N11_DECISION_GATE"

    # Verify that N1 comes before N2, N4, N5
    idx_map = {nid: i for i, nid in enumerate(topo_order)}
    assert idx_map["N1_SCENARIO_LEVERS"] < idx_map["N2_DEMAND_FORECAST"]
    assert idx_map["N1_SCENARIO_LEVERS"] < idx_map["N4_LOGISTICS_RISK"]
    assert idx_map["N1_SCENARIO_LEVERS"] < idx_map["N5_WORKFORCE_BURNOUT"]
    assert idx_map["N2_DEMAND_FORECAST"] < idx_map["N3_VOLUME_COUPLING"]
    assert idx_map["N9_NET_PROFIT"] < idx_map["N11_DECISION_GATE"]
    assert idx_map["N10_COMPOSITE_RISK"] < idx_map["N11_DECISION_GATE"]

    # Verify ancestors and descendants
    ancestors_profit = graph.get_ancestors("N9_NET_PROFIT")
    assert "N1_SCENARIO_LEVERS" in ancestors_profit
    assert "N2_DEMAND_FORECAST" in ancestors_profit
    assert "N3_VOLUME_COUPLING" in ancestors_profit
    assert "N4_LOGISTICS_RISK" in ancestors_profit
    assert "N5_WORKFORCE_BURNOUT" in ancestors_profit

    descendants_levers = graph.get_descendants("N1_SCENARIO_LEVERS")
    assert "N11_DECISION_GATE" in descendants_levers
    assert "N9_NET_PROFIT" in descendants_levers

    # Verify adjacency matrix
    adj, node_ids = graph.adjacency_matrix()
    assert adj.shape == (11, 11)
    assert np.all(np.diag(adj) == 0)  # No self-loops


def test_propagation_operator_state_evaluation():
    """Verifies that StatePropagationOperator evaluates states deterministically and produces valid outputs."""
    op = StatePropagationOperator()
    levers = ScenarioLevers(
        scenario_name="TestStateProp",
        promo_active=True,
        demand_growth_pct=15.0,
        scheduled_days_offset=0,
        shipping_mode_override="Standard Class",
        overtime_workforce_pct=40.0,
    )

    state_vec1, run1, imp1, rec1 = op.evaluate_state(levers)
    state_vec2, run2, imp2, rec2 = op.evaluate_state(levers)

    # Determinism check: identical inputs yield identical states
    assert state_vec1.distance_to(state_vec2) == 0.0
    assert np.array_equal(state_vec1.to_numpy(), state_vec2.to_numpy())
    assert state_vec1.net_profit_delta < 0.0  # Canonical scenario loss verified
    assert rec1.decision_category.value == "REJECT_RESTRUCTURE"


def test_propagation_operator_sensitivity_jacobian():
    """Verifies calculation of the numerical Jacobian matrix J in R^(24 x 3)."""
    op = StatePropagationOperator()
    base_levers = ScenarioLevers(
        scenario_name="TestJacobian",
        promo_active=True,
        demand_growth_pct=10.0,
        scheduled_days_offset=0,
        shipping_mode_override="Standard Class",
        overtime_workforce_pct=30.0,
    )

    jacobian, row_names, col_names = op.compute_sensitivity_jacobian(base_levers, epsilon=1.0)
    assert jacobian.shape == (24, 3)
    assert not np.isnan(jacobian).any()
    assert not np.isinf(jacobian).any()

    # Increasing demand growth should increase projected sales (d Sales / d Demand > 0)
    sales_scen_idx = row_names.index("sales_scenario")
    assert jacobian[sales_scen_idx, 0] > 0.0

    # Increasing overtime percentage should increase workforce cost delta (d Cost / d OT > 0)
    wf_cost_idx = row_names.index("workforce_cost_delta")
    assert jacobian[wf_cost_idx, 2] > 0.0
