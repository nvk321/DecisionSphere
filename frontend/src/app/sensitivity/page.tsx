"use client";

import * as React from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { sensitivityApi } from "@/lib/api/sensitivity";
import { scenariosApi } from "@/lib/api/scenarios";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { formatCurrency, formatPercent, formatDelta } from "@/lib/utils";
import {
  FlaskConical,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Play,
  Layers,
  CheckCircle2,
  Info,
  Sliders,
} from "lucide-react";

export default function SensitivityLabPage() {
  const [activeTab, setActiveTab] = React.useState("demand-sweep");

  // Query scenarios for context binding
  const { data: scenariosData } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => scenariosApi.list({ limit: 20 }),
  });

  const [selectedScenarioId, setSelectedScenarioId] = React.useState("");

  React.useEffect(() => {
    if (!selectedScenarioId && scenariosData?.items && scenariosData.items.length > 0) {
      setSelectedScenarioId(scenariosData.items[0].id);
    }
  }, [scenariosData, selectedScenarioId]);

  // ==========================================
  // EXPERIMENT 1: Demand Shock Sweep (Exp B)
  // ==========================================
  const demandShocks = [-40, -20, -10, 0, 10, 20, 30, 40, 60, 80, 100];
  const demandSweepMutation = useMutation({
    mutationFn: () =>
      sensitivityApi.demandSweep({
        shock_percentages: demandShocks,
      }),
  });

  // ==========================================
  // EXPERIMENT 2: Financial Sweep (Exp D)
  // ==========================================
  const [financialParam, setFinancialParam] = React.useState("asm_001_delay_penalty");
  const financialSweepMutation = useMutation({
    mutationFn: () => {
      let candidateValues: number[] = [];
      if (financialParam === "asm_001_delay_penalty") {
        candidateValues = [10, 15, 20, 25, 30, 40, 50, 60];
      } else if (financialParam === "asm_002_expedite_fee") {
        candidateValues = [5, 10, 15, 20, 25, 30, 35];
      } else if (financialParam === "asm_003_cancellation_factor") {
        candidateValues = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40];
      } else if (financialParam === "asm_004_replacement_cost") {
        candidateValues = [15000, 20000, 30000, 40000, 50000, 60000];
      } else if (financialParam === "asm_005_overtime_rate") {
        candidateValues = [30, 35, 40, 45, 50, 60, 70, 75];
      } else if (financialParam === "cogs_ratio") {
        candidateValues = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90];
      } else {
        candidateValues = [0.4, 0.5, 0.6, 0.7, 0.8];
      }

      return sensitivityApi.financialSweep({
        parameter_name: financialParam,
        candidate_values: candidateValues,
      });
    },
  });

  // ==========================================
  // EXPERIMENT 3: CRS Simplex Weight Sweep
  // ==========================================
  const crsSweepMutation = useMutation({
    mutationFn: () => {
      const candidateWeights = [
        { w_supply: 0.4, w_workforce: 0.4, w_demand: 0.2 }, // Baseline
        { w_supply: 0.6, w_workforce: 0.2, w_demand: 0.2 }, // Supply-chain priority
        { w_supply: 0.2, w_workforce: 0.6, w_demand: 0.2 }, // Workforce priority
        { w_supply: 0.3333, w_workforce: 0.3333, w_demand: 0.3334 }, // Equal balance
        { w_supply: 0.1, w_workforce: 0.1, w_demand: 0.8 }, // Demand priority
      ];
      return sensitivityApi.crsSweep({
        candidate_weights: candidateWeights,
        tau_risk: 50.0,
      });
    },
  });

  // ==========================================
  // EXPERIMENT 4: Tipping Point Search
  // ==========================================
  const [tippingParam, setTippingParam] = React.useState("asm_005_overtime_rate");
  const tippingMutation = useMutation({
    mutationFn: () => {
      let values = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75];
      if (tippingParam === "asm_001_delay_penalty") {
        values = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60];
      } else if (tippingParam === "asm_002_expedite_fee") {
        values = [5, 10, 15, 20, 25, 30, 35];
      } else if (tippingParam === "asm_004_replacement_cost") {
        values = [15000, 20000, 25000, 30000, 40000, 50000, 60000];
      }
      return sensitivityApi.tippingPoint({
        parameter_name: tippingParam,
        candidate_values: values,
      });
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sensitivity Lab"
        description="Stress-test organizational assumptions, evaluate response curves, and identify decision tipping points across non-linear operational domains."
        epistemicNote="Sensitivity analyses assess the robustness of model inferences against shifting business realities."
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 md:grid-cols-4 w-full h-auto p-1 gap-1">
          <TabsTrigger value="demand-sweep">Demand Response Curve</TabsTrigger>
          <TabsTrigger value="financial-sweep">Financial Sensitivity</TabsTrigger>
          <TabsTrigger value="crs-sweep">CRS Weight Stability</TabsTrigger>
          <TabsTrigger value="tipping-point">Tipping Point Analyzer</TabsTrigger>
        </TabsList>

        {/* TAB 1: Demand Response Curve (Experiment B) */}
        <TabsContent value="demand-sweep" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <FlaskConical className="h-4 w-4 text-primary" />
                  Experiment B: Retail Demand Shock Response Curves
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Evaluates how retail sales shocks propagate into logistics delivery delays and employee attrition.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => demandSweepMutation.mutate()}
                disabled={demandSweepMutation.isPending}
              >
                <Play className="h-3.5 w-3.5 mr-1" />
                {demandSweepMutation.isPending ? "Evaluating..." : "Run Experiment B"}
              </Button>
            </CardHeader>

            <CardContent className="space-y-6">
              {demandSweepMutation.error && (
                <ErrorBanner
                  title="Experiment Failed"
                  message={(demandSweepMutation.error as Error).message}
                />
              )}

              {/* Interpretation Panel */}
              <div className="rounded-md border border-border/80 bg-muted/30 p-3.5 text-xs text-foreground/90 space-y-1">
                <div className="flex items-center gap-1.5 font-bold text-primary">
                  <Info className="h-3.5 w-3.5" />
                  Analytical Hypothesis (H2)
                </div>
                <p className="leading-relaxed text-muted-foreground">
                  Coupling demand increases to logistics volume triggers non-linear delivery risk escalations due to carrier capacity limits. Attrition elevates under high demand when mandatory overtime is mandated.
                </p>
              </div>

              {demandSweepMutation.data && (
                <div className="space-y-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Demand Shock</TableHead>
                        <TableHead>Demand Forecast</TableHead>
                        <TableHead>Logistics Delivery Delay Risk</TableHead>
                        <TableHead>Workforce Attrition Risk</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {demandSweepMutation.data.map((item) => (
                        <TableRow key={item.shock_pct}>
                          <TableCell className="font-mono text-xs font-bold">
                            {formatPercent(item.shock_pct, { showSign: true })}
                          </TableCell>
                          <TableCell className="font-mono text-xs tabular-nums">
                            {Math.round(item.demand_forecast).toLocaleString()} Units
                          </TableCell>
                          <TableCell className="font-mono text-xs tabular-nums text-amber-300">
                            {formatPercent(item.late_delivery_risk, { isRatio: true })}
                          </TableCell>
                          <TableCell className="font-mono text-xs tabular-nums text-rose-300">
                            {formatPercent(item.workforce_attrition_risk, { isRatio: true })}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              {!demandSweepMutation.data && !demandSweepMutation.isPending && (
                <div className="text-center py-10 text-xs text-muted-foreground border border-dashed rounded-md">
                  Click &quot;Run Experiment B&quot; to evaluate demand shock response curves across $[-50\%, +100\%]$.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 2: Financial Parameter Sweep (Experiment D) */}
        <TabsContent value="financial-sweep" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <FlaskConical className="h-4 w-4 text-primary" />
                  Experiment D: Parametric Financial Sensitivity
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Determines at what operational cost levels a strategic decision ceases to be profitable.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => financialSweepMutation.mutate()}
                disabled={financialSweepMutation.isPending}
              >
                <Play className="h-3.5 w-3.5 mr-1" />
                {financialSweepMutation.isPending ? "Sweeping..." : "Execute 1D Sweep"}
              </Button>
            </CardHeader>

            <CardContent className="space-y-6">
              {financialSweepMutation.error && (
                <ErrorBanner
                  title="Financial Sweep Failed"
                  message={(financialSweepMutation.error as Error).message}
                />
              )}

              <div className="flex items-center gap-3 max-w-sm">
                <label className="text-xs font-semibold text-foreground whitespace-nowrap">
                  Parameter to Sweep:
                </label>
                <Select
                  value={financialParam}
                  onChange={(e) => setFinancialParam(e.target.value)}
                >
                  <option value="asm_001_delay_penalty">ASM-001: Carrier Delay Penalty ($/order)</option>
                  <option value="asm_002_expedite_fee">ASM-002: Expedited Freight Fee ($/order)</option>
                  <option value="asm_004_replacement_cost">ASM-004: Turnover Replacement ($/worker)</option>
                  <option value="asm_005_overtime_rate">ASM-005: Overtime Labor Wage ($/hr)</option>
                  <option value="cogs_ratio">COGS Ratio on Realized Sales</option>
                </Select>
              </div>

              {financialSweepMutation.data && (
                <div className="space-y-4">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Parameter Value</TableHead>
                        <TableHead>Projected Net Profit Delta</TableHead>
                        <TableHead>Economic Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {financialSweepMutation.data.map((item, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-mono text-xs font-bold text-foreground">
                            {item.parameter_name.includes("ratio")
                              ? formatPercent(item.value, { isRatio: true })
                              : `$${item.value.toLocaleString()}`}
                          </TableCell>
                          <TableCell
                            className={`font-mono text-xs font-bold tabular-nums ${
                              item.is_profitable ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            {formatCurrency(item.net_profit_delta, { showSign: true })}
                          </TableCell>
                          <TableCell>
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                                item.is_profitable
                                  ? "border-emerald-600 bg-emerald-950/40 text-emerald-300"
                                  : "border-rose-600 bg-rose-950/40 text-rose-300"
                              }`}
                            >
                              {item.is_profitable ? "PROFITABLE" : "UNPROFITABLE"}
                            </span>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}

              {!financialSweepMutation.data && !financialSweepMutation.isPending && (
                <div className="text-center py-10 text-xs text-muted-foreground border border-dashed rounded-md">
                  Select a coupling parameter and click &quot;Execute 1D Sweep&quot; to evaluate bottom-line trajectory.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 3: CRS Simplex Weight Stability */}
        <TabsContent value="crs-sweep" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <FlaskConical className="h-4 w-4 text-primary" />
                  CRS Multi-Criteria Weight Stability
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Validates whether the executive recommendation holds when organizational priorities shift.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => crsSweepMutation.mutate()}
                disabled={crsSweepMutation.isPending}
              >
                <Play className="h-3.5 w-3.5 mr-1" />
                {crsSweepMutation.isPending ? "Testing..." : "Test Stability"}
              </Button>
            </CardHeader>

            <CardContent className="space-y-6">
              {crsSweepMutation.error && (
                <ErrorBanner
                  title="Simplex Sweep Failed"
                  message={(crsSweepMutation.error as Error).message}
                />
              )}

              {crsSweepMutation.data && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Domain Priority Weightings (w_s, w_w, w_d)</TableHead>
                      <TableHead>Composite Risk Score</TableHead>
                      <TableHead>Risk Tier</TableHead>
                      <TableHead>Strategic Recommendation</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {crsSweepMutation.data.map((item, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-mono text-xs">
                          SC: {formatPercent(item.w_supply, { isRatio: true })}, WF:{" "}
                          {formatPercent(item.w_workforce, { isRatio: true })}, Demand:{" "}
                          {formatPercent(item.w_demand, { isRatio: true })}
                        </TableCell>
                        <TableCell className="font-mono text-xs tabular-nums font-bold">
                          {item.composite_risk_score.toFixed(1)}
                        </TableCell>
                        <TableCell className="text-xs font-semibold">
                          {item.risk_level}
                        </TableCell>
                        <TableCell className="font-bold text-xs">
                          {item.decision_category}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}

              {!crsSweepMutation.data && !crsSweepMutation.isPending && (
                <div className="text-center py-10 text-xs text-muted-foreground border border-dashed rounded-md">
                  Click &quot;Test Stability&quot; to sweep alternative domain weighting simplex configurations.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 4: Tipping Point Analyzer */}
        <TabsContent value="tipping-point" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  Decision Boundary Tipping Point Search
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Pinpoints exact threshold where executive decision flips from PROCEED to REJECT.
                </p>
              </div>
              <Button
                size="sm"
                onClick={() => tippingMutation.mutate()}
                disabled={tippingMutation.isPending}
              >
                <Play className="h-3.5 w-3.5 mr-1" />
                {tippingMutation.isPending ? "Searching..." : "Search Boundary"}
              </Button>
            </CardHeader>

            <CardContent className="space-y-6">
              {tippingMutation.error && (
                <ErrorBanner
                  title="Search Failed"
                  message={(tippingMutation.error as Error).message}
                />
              )}

              <div className="flex items-center gap-3 max-w-sm">
                <label className="text-xs font-semibold text-foreground whitespace-nowrap">
                  Inspect Parameter:
                </label>
                <Select
                  value={tippingParam}
                  onChange={(e) => setTippingParam(e.target.value)}
                >
                  <option value="asm_005_overtime_rate">ASM-005: Overtime Hourly Rate ($/hr)</option>
                  <option value="asm_001_delay_penalty">ASM-001: Carrier Delay Penalty ($/order)</option>
                </Select>
              </div>

              {tippingMutation.data && (
                <div className="p-4 rounded-lg border border-border bg-muted/20 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-foreground">
                      Boundary Search Result:
                    </span>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded border ${
                        tippingMutation.data.flip_detected
                          ? "border-amber-600 bg-amber-950/40 text-amber-300"
                          : "border-emerald-600 bg-emerald-950/40 text-emerald-300"
                      }`}
                    >
                      {tippingMutation.data.flip_detected ? "TIPPING POINT DETECTED" : "NO FLIP FOUND"}
                    </span>
                  </div>

                  {tippingMutation.data.flip_detected ? (
                    <div className="space-y-2 text-xs">
                      <p className="text-foreground leading-relaxed">
                        The strategic decision category flips at{" "}
                        <strong className="font-mono text-primary">
                          ${tippingMutation.data.flip_value}
                        </strong>{" "}
                        from{" "}
                        <span className="text-amber-400 font-bold">
                          {tippingMutation.data.previous_category}
                        </span>{" "}
                        to{" "}
                        <span className="text-rose-400 font-bold">
                          {tippingMutation.data.new_category}
                        </span>
                        .
                      </p>
                      <div className="flex items-center gap-4 text-muted-foreground pt-1">
                        <span>
                          Net Profit at Flip:{" "}
                          <strong className="text-foreground font-mono">
                            {formatCurrency(tippingMutation.data.net_profit_delta, { showSign: true })}
                          </strong>
                        </span>
                        <span>
                          CRS at Flip:{" "}
                          <strong className="text-foreground font-mono">
                            {tippingMutation.data.composite_risk_score?.toFixed(1)}
                          </strong>
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      The decision category remained stable across the entire tested candidate range.
                    </p>
                  )}
                </div>
              )}

              {!tippingMutation.data && !tippingMutation.isPending && (
                <div className="text-center py-10 text-xs text-muted-foreground border border-dashed rounded-md">
                  Click &quot;Search Boundary&quot; to detect parameter thresholds triggering strategic rejection.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
