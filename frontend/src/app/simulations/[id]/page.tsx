"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { simulationsApi } from "@/lib/api/simulations";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import {
  DECISION_CATEGORIES,
  DecisionCategory,
  RISK_LEVELS,
  RiskLevel,
} from "@/lib/constants";
import {
  formatCurrency,
  formatPercent,
  formatDelta,
  formatDate,
  truncateId,
  copyToClipboard,
} from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  Sliders,
  FlaskConical,
  Layers,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  AlertOctagon,
  FileCheck,
  CheckCircle2,
} from "lucide-react";

export default function SimulationDetailPage() {
  const params = useParams();
  const runId = params.id as string;
  const [provenanceOpen, setProvenanceOpen] = React.useState(false);
  const [copiedHash, setCopiedHash] = React.useState<string | null>(null);

  const { data: run, isLoading, error, refetch } = useQuery({
    queryKey: ["simulation", runId],
    queryFn: () => simulationsApi.getById(runId),
  });

  const handleCopy = async (text: string, key: string) => {
    const ok = await copyToClipboard(text);
    if (ok) {
      setCopiedHash(key);
      setTimeout(() => setCopiedHash(null), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <CardSkeleton className="h-48" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CardSkeleton className="h-36" />
          <CardSkeleton className="h-36" />
          <CardSkeleton className="h-36" />
        </div>
        <CardSkeleton className="h-64" />
      </div>
    );
  }

  if (error || !run) {
    return (
      <ErrorBanner
        title="Failed to Load Simulation Analysis"
        message={(error as Error)?.message || "Simulation run not found."}
        onRetry={() => refetch()}
      />
    );
  }

  const rec = run.recommendation_result;
  const fin = run.financial_result;
  const predictions = run.domain_predictions || [];

  const decisionCat = (rec?.decision_category || "PROCEED_WITH_MITIGATIONS") as DecisionCategory;
  const decisionMeta = DECISION_CATEGORIES[decisionCat] || DECISION_CATEGORIES.PROCEED_WITH_MITIGATIONS;

  const crs = rec?.composite_risk_score ?? 0;
  const riskLvl = (rec?.risk_level || "MODERATE") as RiskLevel;
  const riskMeta = RISK_LEVELS[riskLvl] || RISK_LEVELS.MODERATE;

  const netProfit = fin?.net_profit_delta ?? 0;
  const isProfitable = netProfit >= 0;

  // Domain predictions mapping
  const demandPred = predictions.find((p) => p.domain === "DEMAND");
  const scPred = predictions.find((p) => p.domain === "SUPPLY_CHAIN");
  const wfPred = predictions.find((p) => p.domain === "WORKFORCE");

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <PageHeader
        title="Decision Analysis & Multi-Domain Evaluation"
        description={`Authoritative simulation results for run ${truncateId(run.id, 8)}. Evaluated with verified models and deterministic managerial accounting.`}
        epistemicNote="Outputs combine PREDICTED inferences, CALCULATED accounting, and RECOMMENDED actions."
        actions={
          <div className="flex items-center gap-2">
            <Link href={`/sensitivity?scenario_version_id=${run.scenario_version_id}&policy_id=${run.policy_id}`}>
              <Button variant="outline" size="sm">
                <FlaskConical className="h-4 w-4 mr-1.5" />
                Sensitivity Lab
              </Button>
            </Link>
            <Link href="/simulate">
              <Button size="sm">
                <Sliders className="h-4 w-4 mr-1.5" />
                Simulate Another
              </Button>
            </Link>
          </div>
        }
      />

      {/* SECTION A & B: Executive Decision & Composite Risk Score */}
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border/60">
          <div className="space-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              SYNTHESIZED STRATEGIC DIRECTIVE
            </span>
            <div className="flex items-center gap-3">
              <span
                className={`inline-flex items-center px-4 py-1.5 rounded-lg border text-base font-extrabold tracking-wide ${decisionMeta.badgeClass}`}
              >
                {decisionMeta.label}
              </span>
              <EpistemicBadge tier="RECOMMENDED" />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
                COMPOSITE RISK SCORE
              </span>
              <div className="flex items-center justify-end gap-1.5 mt-0.5">
                <span className="text-2xl font-black text-foreground tabular-nums">
                  {crs.toFixed(1)}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border ${riskMeta.badgeClass}`}
                >
                  {riskMeta.label}
                </span>
              </div>
            </div>

            <div className="text-right pl-4 border-l border-border/60">
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
                NET PROFIT IMPACT
              </span>
              <div
                className={`text-2xl font-black tabular-nums mt-0.5 ${
                  isProfitable ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {formatCurrency(netProfit, { showSign: true, compact: true })}
              </div>
            </div>
          </div>
        </div>

        {/* Executive Synthesis Statement */}
        <div className="space-y-3">
          <p className="text-sm text-foreground/90 leading-relaxed font-medium">
            {rec?.executive_briefing || decisionMeta.summary}
          </p>

          {rec?.primary_vulnerability && (
            <div className="rounded-md border border-amber-800/40 bg-amber-950/20 p-3 flex items-start gap-2.5 text-xs text-amber-300">
              <ShieldAlert className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
              <div>
                <span className="font-bold">Primary Operational Bottleneck: </span>
                <span>{rec.primary_vulnerability}</span>
              </div>
            </div>
          )}

          {/* Operational Strain Decomposition */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="rounded border border-border/60 bg-muted/20 p-3">
              <span className="text-[11px] text-muted-foreground block">
                Logistics Delivery Strain (w=40%)
              </span>
              <span className="font-mono font-bold text-base text-foreground tabular-nums">
                {(rec?.supply_chain_strain ?? 0).toFixed(1)}
                <span className="text-xs font-normal text-muted-foreground"> / 100</span>
              </span>
            </div>

            <div className="rounded border border-border/60 bg-muted/20 p-3">
              <span className="text-[11px] text-muted-foreground block">
                Workforce Attrition Strain (w=40%)
              </span>
              <span className="font-mono font-bold text-base text-foreground tabular-nums">
                {(rec?.workforce_strain ?? 0).toFixed(1)}
                <span className="text-xs font-normal text-muted-foreground"> / 100</span>
              </span>
            </div>

            <div className="rounded border border-border/60 bg-muted/20 p-3">
              <span className="text-[11px] text-muted-foreground block">
                Demand Volatility Strain (w=20%)
              </span>
              <span className="font-mono font-bold text-base text-foreground tabular-nums">
                {(rec?.demand_strain ?? 0).toFixed(1)}
                <span className="text-xs font-normal text-muted-foreground"> / 100</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION E: Operational Domain Evidence */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              Cross-Domain Predictive Evidence
            </h2>
            <p className="text-xs text-muted-foreground">
              Independent machine learning inference models conditioned on applied what-if levers.
            </p>
          </div>
          <EpistemicBadge tier="PREDICTED" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Demand Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Commercial Demand</CardTitle>
              <p className="text-[11px] text-muted-foreground">XGBoost Regressor (WAPE 8.12%)</p>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-muted-foreground">Projected Sales:</span>
                <span className="font-mono font-bold text-lg text-foreground tabular-nums">
                  {demandPred ? `${Math.round(demandPred.scenario_value).toLocaleString()} Units` : "N/A"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs pt-1 border-t border-border/40">
                <span className="text-muted-foreground">Baseline Volume:</span>
                <span className="font-mono tabular-nums">
                  {demandPred ? `${Math.round(demandPred.baseline_value).toLocaleString()} Units` : "—"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs">
                <span className="text-muted-foreground">Delta Shift:</span>
                <span className="font-mono font-semibold text-emerald-400 tabular-nums">
                  {demandPred ? formatDelta(demandPred.delta_value, "Units", 0) : "—"}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Supply Chain Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Logistics Delivery Risk</CardTitle>
              <p className="text-[11px] text-muted-foreground">Calibrated XGBoost (ROC-AUC 0.7795)</p>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-muted-foreground">Scenario Late Probability:</span>
                <span className="font-mono font-bold text-lg text-foreground tabular-nums">
                  {scPred ? formatPercent(scPred.scenario_value, { isRatio: true }) : "N/A"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs pt-1 border-t border-border/40">
                <span className="text-muted-foreground">Historical Baseline:</span>
                <span className="font-mono tabular-nums">
                  {scPred ? formatPercent(scPred.baseline_value, { isRatio: true }) : "—"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs">
                <span className="text-muted-foreground">Risk Delta:</span>
                <span
                  className={`font-mono font-semibold tabular-nums ${
                    scPred && scPred.delta_value > 0 ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {scPred ? formatDelta((scPred.scenario_value - scPred.baseline_value) * 100, "pp", 1) : "—"}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Workforce Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Workforce Attrition Risk</CardTitle>
              <p className="text-[11px] text-muted-foreground">Calibrated XGBoost (ROC-AUC 0.8045)</p>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-muted-foreground">Scenario Attrition Rate:</span>
                <span className="font-mono font-bold text-lg text-foreground tabular-nums">
                  {wfPred ? formatPercent(wfPred.scenario_value, { isRatio: true }) : "N/A"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs pt-1 border-t border-border/40">
                <span className="text-muted-foreground">Cohort Baseline:</span>
                <span className="font-mono tabular-nums">
                  {wfPred ? formatPercent(wfPred.baseline_value, { isRatio: true }) : "—"}
                </span>
              </div>
              <div className="flex items-baseline justify-between text-xs">
                <span className="text-muted-foreground">Attrition Delta:</span>
                <span
                  className={`font-mono font-semibold tabular-nums ${
                    wfPred && wfPred.delta_value > 0 ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {wfPred ? formatDelta((wfPred.scenario_value - wfPred.baseline_value) * 100, "pp", 1) : "—"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* SECTION C: Managerial Financial Waterfall */}
      {fin && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Managerial Income Statement & Cost Breakdown
              </h2>
              <p className="text-xs text-muted-foreground">
                Traceable deterministic accounting formulas linking operational shocks to enterprise bottom line.
              </p>
            </div>
            <EpistemicBadge tier="CALCULATED" />
          </div>

          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Financial Line Item</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Epistemic Status</TableHead>
                    <TableHead className="text-right">Monetary Delta (USD)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {/* Detailed Line Items */}
                  {fin.line_items?.map((item, idx) => {
                    const isPositive = item.amount >= 0;
                    const isExpense = item.category === "EXPENSE";

                    return (
                      <TableRow key={idx}>
                        <TableCell className="font-medium text-xs text-foreground">
                          {item.line_item_name}
                        </TableCell>
                        <TableCell className="text-xs font-mono text-muted-foreground">
                          {item.category}
                        </TableCell>
                        <TableCell>
                          <EpistemicBadge tier={item.epistemic_tier} showIcon={false} />
                        </TableCell>
                        <TableCell
                          className={`text-right font-mono text-xs tabular-nums font-semibold ${
                            isExpense
                              ? "text-rose-300"
                              : isPositive
                              ? "text-emerald-400"
                              : "text-rose-400"
                          }`}
                        >
                          {formatCurrency(item.amount, { showSign: true })}
                        </TableCell>
                      </TableRow>
                    );
                  })}

                  {/* Summary Net Profit Row */}
                  <TableRow className="border-t-2 border-border bg-muted/50 font-bold">
                    <TableCell className="text-sm font-extrabold text-foreground" colSpan={2}>
                      NET OPERATING PROFIT DELTA (&Delta; Profit)
                    </TableCell>
                    <TableCell>
                      <EpistemicBadge tier="CALCULATED" />
                    </TableCell>
                    <TableCell
                      className={`text-right font-mono text-sm tabular-nums font-black ${
                        isProfitable ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {formatCurrency(netProfit, { showSign: true })}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {/* SECTION F: Rule-Grounded Strategic Recommendations */}
      {rec?.strategic_actions && rec.strategic_actions.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Prioritized Strategic Interventions
              </h2>
              <p className="text-xs text-muted-foreground">
                Deterministic condition-triggered actions with non-causal trade-off disclosures.
              </p>
            </div>
            <EpistemicBadge tier="RECOMMENDED" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {rec.strategic_actions.map((act) => {
              const severityColorMap: Record<string, string> = {
                CRITICAL: "border-rose-600/80 bg-rose-950/20 text-rose-300",
                HIGH: "border-orange-600/80 bg-orange-950/20 text-orange-300",
                MEDIUM: "border-amber-600/80 bg-amber-950/20 text-amber-300",
                LOW: "border-emerald-600/80 bg-emerald-950/20 text-emerald-300",
              };

              return (
                <div
                  key={act.action_id}
                  className="rounded-lg border border-border bg-card p-4 space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-bold text-foreground">
                        {act.action_id}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          severityColorMap[act.severity] || "border-border text-foreground"
                        }`}
                      >
                        {act.severity} PRIORITY
                      </span>
                    </div>

                    <h4 className="font-bold text-sm text-foreground">{act.title}</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {act.description}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-border/50 space-y-1 text-[11px]">
                    <div className="text-muted-foreground">
                      <span className="font-semibold text-foreground/80">Trigger Rule: </span>
                      <span className="font-mono">{act.trigger_rule_id}</span> ({act.domain})
                    </div>
                    <div className="rounded bg-muted/40 p-2 text-foreground/90 font-medium">
                      <span className="text-amber-400 font-bold">Trade-Off: </span>
                      <span>{act.expected_trade_off}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* SECTION H: Cryptographic Provenance Accordion (Gate H) */}
      <div className="rounded-lg border border-border bg-card overflow-hidden">
        <button
          type="button"
          onClick={() => setProvenanceOpen(!provenanceOpen)}
          className="w-full flex items-center justify-between p-4 bg-muted/30 hover:bg-muted/50 text-left transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <FileCheck className="h-4 w-4 text-primary" />
            <span className="font-semibold text-sm text-foreground">
              Cryptographic Provenance Signature Tuple (&Sigma;<sub>run</sub>)
            </span>
            <span className="text-xs text-muted-foreground font-mono hidden sm:inline">
              (Gate H Verification)
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{provenanceOpen ? "Hide Details" : "Inspect Signature"}</span>
            {provenanceOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </div>
        </button>

        {provenanceOpen && run.audit_record && (
          <div className="p-4 space-y-4 text-xs font-mono bg-card">
            <p className="text-muted-foreground font-sans leading-relaxed">
              This simulation run is permanently sealed with an 8-element cryptographic tuple guaranteeing reproducible execution, artifact immutability, and academic auditability.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 rounded border border-border/60 bg-muted/20 space-y-1">
                <span className="text-muted-foreground block text-[11px] font-sans font-semibold">
                  Scenario Version ID
                </span>
                <span className="text-foreground break-all">{run.scenario_version_id}</span>
              </div>

              <div className="p-3 rounded border border-border/60 bg-muted/20 space-y-1">
                <span className="text-muted-foreground block text-[11px] font-sans font-semibold">
                  Assumption Policy ID
                </span>
                <span className="text-foreground break-all">{run.policy_id}</span>
              </div>

              <div className="p-3 rounded border border-border/60 bg-muted/20 space-y-1">
                <span className="text-muted-foreground block text-[11px] font-sans font-semibold">
                  Git Commit SHA
                </span>
                <div className="flex items-center justify-between">
                  <span className="text-foreground">
                    {run.audit_record.git_commit_hash || "N/A"}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopy(run.audit_record!.git_commit_hash || "", "git")}
                    className="p-1 hover:text-foreground text-muted-foreground"
                    title="Copy Git SHA"
                  >
                    {copiedHash === "git" ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                  </button>
                </div>
              </div>

              <div className="p-3 rounded border border-border/60 bg-muted/20 space-y-1">
                <span className="text-muted-foreground block text-[11px] font-sans font-semibold">
                  Execution Timestamp (UTC)
                </span>
                <span className="text-foreground">{formatDate(run.executed_at)}</span>
              </div>
            </div>

            {/* Serialized Model Fingerprints */}
            <div className="space-y-2 pt-2">
              <span className="font-sans font-bold text-xs text-foreground block">
                Serialized Machine Learning Model Artifact SHA-256 Hashes
              </span>
              <div className="space-y-1.5">
                {Object.entries(run.audit_record.model_hashes || {}).map(([key, hash]) => (
                  <div
                    key={key}
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-2 rounded border border-border/40 bg-muted/30 text-[11px]"
                  >
                    <span className="font-semibold text-primary capitalize">{key} Model:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground break-all">{hash}</span>
                      <button
                        type="button"
                        onClick={() => handleCopy(hash, key)}
                        className="p-1 hover:text-foreground text-muted-foreground cursor-pointer"
                        title="Copy Hash"
                      >
                        {copiedHash === key ? (
                          <Check className="h-3 w-3 text-emerald-400" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
