"""
DecisionSphere — Formal State-Space Dependency Graph Architecture
Defines the directed dependency graph G = (V, E) governing cross-domain state transitions,
topological execution ordering, and backward/forward lineage tracing.
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class DependencyNode:
    """
    Represents an atomic state node v in V within the enterprise dependency graph.
    """
    node_id: str
    name: str
    domain: str
    epistemic_tier: str  # OBSERVED, PREDICTED, ASSUMED, PROPAGATED, CALCULATED, RECOMMENDED
    dimension_indices: Tuple[int, ...]
    description: str


@dataclass(frozen=True)
class DependencyEdge:
    """
    Represents a directed dependency edge e = (u, v) in E with associated transfer semantics.
    """
    source_id: str
    target_id: str
    coupling_parameter: Optional[str] = None  # e.g., ASM-001, ASM-007
    transfer_type: str = "deterministic"  # deterministic, statistical_ml, lexicographic
    description: str = ""


class ScenarioDependencyGraph:
    """
    Directed Acyclic Graph (DAG) G = (V, E) representing the formal cross-domain
    coupling topology of DecisionSphere.
    
    Guarantees:
    - Formal verification of acyclicity (zero circular dependencies).
    - Topological sorting for strictly ordered pipeline execution.
    - Full backward ancestor and forward descendant lineage tracing.
    """

    def __init__(self):
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: List[DependencyEdge] = []
        self._adjacency: Dict[str, List[str]] = {}
        self._reverse_adjacency: Dict[str, List[str]] = {}
        self._build_canonical_graph()

    def _build_canonical_graph(self) -> None:
        """Constructs the canonical 11-node enterprise dependency topology."""
        nodes = [
            DependencyNode(
                node_id="N1_SCENARIO_LEVERS",
                name="Scenario Interventions U",
                domain="Scenario Specification",
                epistemic_tier="ASSUMED",
                dimension_indices=(9, 10, 14, 15),
                description="User-defined commercial shocks, logistics offsets, and overtime targets.",
            ),
            DependencyNode(
                node_id="N2_DEMAND_FORECAST",
                name="Retail Demand Forecast Y_sales",
                domain="Retail Demand",
                epistemic_tier="PREDICTED",
                dimension_indices=(0, 1, 2, 3),
                description="Autoregressive XGBoost recursive sales forecast.",
            ),
            DependencyNode(
                node_id="N3_VOLUME_COUPLING",
                name="Normalized Order Throughput N_orders",
                domain="Enterprise Normalization",
                epistemic_tier="PROPAGATED",
                dimension_indices=(4, 5),
                description="Temporal cycle alignment (ASM-008) and volume scaling (ASM-007).",
            ),
            DependencyNode(
                node_id="N4_LOGISTICS_RISK",
                name="Logistics Late Delivery Risk p_late",
                domain="Supply Chain",
                epistemic_tier="PREDICTED",
                dimension_indices=(6, 7, 8),
                description="Sigmoid-calibrated late shipment probability.",
            ),
            DependencyNode(
                node_id="N5_WORKFORCE_BURNOUT",
                name="Workforce Attrition Risk p_att",
                domain="Workforce",
                epistemic_tier="PREDICTED",
                dimension_indices=(11, 12, 13),
                description="Sigmoid-calibrated employee attrition probability under overtime strain.",
            ),
            DependencyNode(
                node_id="N6_ACCOUNTING_REVENUE",
                name="Gross & Realized Revenue Accounting",
                domain="Managerial Accounting",
                epistemic_tier="CALCULATED",
                dimension_indices=(16, 17),
                description="Gross sales and stockout fulfillment loss deduction (ASM-003).",
            ),
            DependencyNode(
                node_id="N7_ACCOUNTING_LOGISTICS",
                name="Supply Chain Disruption Costs",
                domain="Managerial Accounting",
                epistemic_tier="CALCULATED",
                dimension_indices=(18,),
                description="Carrier late penalties (ASM-001) and air expedite surcharges (ASM-002).",
            ),
            DependencyNode(
                node_id="N8_ACCOUNTING_LABOR",
                name="Workforce Operational Labor Costs",
                domain="Managerial Accounting",
                epistemic_tier="CALCULATED",
                dimension_indices=(19,),
                description="Turnover replacement costs (ASM-004) and overtime wage premium (ASM-005).",
            ),
            DependencyNode(
                node_id="N9_NET_PROFIT",
                name="Net Operating Profit Delta Delta Pi",
                domain="Managerial Accounting",
                epistemic_tier="CALCULATED",
                dimension_indices=(20,),
                description="Synthesis of revenue, COGS, logistics, and labor expenses.",
            ),
            DependencyNode(
                node_id="N10_COMPOSITE_RISK",
                name="Composite Operational Risk Score CRS",
                domain="Operational Risk",
                epistemic_tier="CALCULATED",
                dimension_indices=(21, 22, 23),
                description="Multi-criteria strain index across logistics, labor, and fulfillment.",
            ),
            DependencyNode(
                node_id="N11_DECISION_GATE",
                name="Lexicographic Decision Gating",
                domain="Strategic Synthesis",
                epistemic_tier="RECOMMENDED",
                dimension_indices=(),
                description="Tri-state strategic decision classification (REJECT, PROCEED, MITIGATE).",
            ),
        ]

        for node in nodes:
            self._nodes[node.node_id] = node
            self._adjacency[node.node_id] = []
            self._reverse_adjacency[node.node_id] = []

        edges = [
            # Lever injections into domain models
            DependencyEdge("N1_SCENARIO_LEVERS", "N2_DEMAND_FORECAST", None, "statistical_ml", "Demand growth & promo levers"),
            DependencyEdge("N1_SCENARIO_LEVERS", "N4_LOGISTICS_RISK", None, "statistical_ml", "Schedule offsets & freight mode"),
            DependencyEdge("N1_SCENARIO_LEVERS", "N5_WORKFORCE_BURNOUT", "ASM-006", "statistical_ml", "Target overtime % & WLB decrement"),
            
            # Demand volume propagation
            DependencyEdge("N2_DEMAND_FORECAST", "N3_VOLUME_COUPLING", "ASM-007,ASM-008", "deterministic", "Sales to normalized order volume"),
            DependencyEdge("N2_DEMAND_FORECAST", "N6_ACCOUNTING_REVENUE", None, "deterministic", "Forecasted volume to gross revenue"),
            
            # Volume to logistics disruption costs
            DependencyEdge("N3_VOLUME_COUPLING", "N7_ACCOUNTING_LOGISTICS", None, "deterministic", "Order volume scaling for late shipments"),
            DependencyEdge("N4_LOGISTICS_RISK", "N6_ACCOUNTING_REVENUE", "ASM-003", "deterministic", "Late delivery to fulfillment loss"),
            DependencyEdge("N4_LOGISTICS_RISK", "N7_ACCOUNTING_LOGISTICS", "ASM-001,ASM-002", "deterministic", "Calibrated p_late to carrier penalty"),
            DependencyEdge("N4_LOGISTICS_RISK", "N10_COMPOSITE_RISK", None, "deterministic", "Late probability to S_supply index"),
            
            # Workforce to labor costs
            DependencyEdge("N5_WORKFORCE_BURNOUT", "N8_ACCOUNTING_LABOR", "ASM-004", "deterministic", "Calibrated p_att to turnover cost"),
            DependencyEdge("N1_SCENARIO_LEVERS", "N8_ACCOUNTING_LABOR", "ASM-005", "deterministic", "Overtime headcount to wage premium"),
            DependencyEdge("N5_WORKFORCE_BURNOUT", "N10_COMPOSITE_RISK", None, "deterministic", "Attrition probability to S_workforce index"),
            
            # Accounting synthesis to Net Profit
            DependencyEdge("N6_ACCOUNTING_REVENUE", "N9_NET_PROFIT", None, "deterministic", "Realized revenue margin"),
            DependencyEdge("N7_ACCOUNTING_LOGISTICS", "N9_NET_PROFIT", None, "deterministic", "Logistics expense subtraction"),
            DependencyEdge("N8_ACCOUNTING_LABOR", "N9_NET_PROFIT", None, "deterministic", "Labor expense subtraction"),
            
            # Final strategic decision synthesis
            DependencyEdge("N1_SCENARIO_LEVERS", "N10_COMPOSITE_RISK", None, "deterministic", "Commercial shock to S_demand index"),
            DependencyEdge("N9_NET_PROFIT", "N11_DECISION_GATE", None, "lexicographic", "Financial solvency feasibility gate"),
            DependencyEdge("N10_COMPOSITE_RISK", "N11_DECISION_GATE", None, "lexicographic", "Operational strain tolerance threshold"),
        ]

        for edge in edges:
            self._edges.append(edge)
            self._adjacency[edge.source_id].append(edge.target_id)
            self._reverse_adjacency[edge.target_id].append(edge.source_id)

    @property
    def nodes(self) -> Dict[str, DependencyNode]:
        return dict(self._nodes)

    @property
    def edges(self) -> List[DependencyEdge]:
        return list(self._edges)

    def is_acyclic(self) -> bool:
        """Verifies that the graph contains zero directed cycles (pure DAG)."""
        visited: Dict[str, int] = {k: 0 for k in self._nodes}  # 0: unvisited, 1: visiting, 2: visited

        def dfs(node_id: str) -> bool:
            visited[node_id] = 1
            for neighbor in self._adjacency[node_id]:
                if visited[neighbor] == 1:
                    return False  # Back-edge detected (cycle)
                if visited[neighbor] == 0:
                    if not dfs(neighbor):
                        return False
            visited[node_id] = 2
            return True

        for n_id in self._nodes:
            if visited[n_id] == 0:
                if not dfs(n_id):
                    return False
        return True

    def topological_sort(self) -> List[str]:
        """
        Computes the topological execution ordering of the dependency graph using Kahn's algorithm.
        """
        in_degree = {k: len(self._reverse_adjacency[k]) for k in self._nodes}
        queue = [k for k, d in in_degree.items() if d == 0]
        topo_order: List[str] = []

        while queue:
            curr = queue.pop(0)
            topo_order.append(curr)
            for neighbor in self._adjacency[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topo_order) != len(self._nodes):
            raise RuntimeError("Graph contains a cycle; topological ordering is undefined.")
        return topo_order

    def get_ancestors(self, node_id: str) -> Set[str]:
        """Returns the set of all upstream causal/dependency ancestor nodes for node_id."""
        ancestors: Set[str] = set()

        def recurse(curr: str):
            for parent in self._reverse_adjacency[curr]:
                if parent not in ancestors:
                    ancestors.add(parent)
                    recurse(parent)

        recurse(node_id)
        return ancestors

    def get_descendants(self, node_id: str) -> Set[str]:
        """Returns the set of all downstream impacted descendant nodes for node_id."""
        descendants: Set[str] = set()

        def recurse(curr: str):
            for child in self._adjacency[curr]:
                if child not in descendants:
                    descendants.add(child)
                    recurse(child)

        recurse(node_id)
        return descendants

    def adjacency_matrix(self) -> Tuple[np.ndarray, List[str]]:
        """
        Returns the binary adjacency matrix A in {0, 1}^(N x N) and the ordered node IDs.
        """
        node_ids = list(self._nodes.keys())
        n = len(node_ids)
        idx_map = {nid: i for i, nid in enumerate(node_ids)}
        adj = np.zeros((n, n), dtype=np.int32)

        for edge in self._edges:
            i = idx_map[edge.source_id]
            j = idx_map[edge.target_id]
            adj[i, j] = 1

        return adj, node_ids
