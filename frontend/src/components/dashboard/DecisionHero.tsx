import * as React from "react";
import Link from "next/link";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { DECISION_CATEGORIES, DecisionCategory, RISK_LEVELS, RiskLevel } from "@/lib/constants";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { SimulationDetail } from "@/lib/api/types";
import { ShieldAlert, ArrowUpRight, TrendingUp, TrendingDown, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface DecisionHeroProps {
  simulation: SimulationDetail;
  scenarioName?: string;
  scenarioId?: string;
}

export function DecisionHero({
  simulation,
  scenarioName = "Primary Strategic Scenario",
  scenarioId,
}: DecisionHeroProps) {
  const rec = simulation.recommendation_result;
  const fin = simulation.financial_result;

  const decisionCat = (rec?.decision_category || "PROCEED_WITH_MITIGATIONS") as DecisionCategory;
  const decisionMeta = DECISION_CATEGORIES[decisionCat] || DECISION_CATEGORIES.PROCEED_WITH_MITIGATIONS;

  const crs = rec?.composite_risk_score ?? 0;
  const riskLvl = (rec?.risk_level || "MODERATE") as RiskLevel;
  const riskMeta = RISK_LEVELS[riskLvl] || RISK_LEVELS.MODERATE;

  const netProfit = fin?.net_profit_delta ?? 0;
  const isProfitable = netProfit >= 0;

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
      {/* Top Banner: Scenario Context & Epistemic Demarcation */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-3 border-b border-border/60 bg-muted/30 text-xs">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-primary" />
          <span className="text-muted-foreground uppercase font-bold tracking-wider text-[10px]">
            ACTIVE SIMULATION RUN
          </span>
          <span className="font-semibold text-foreground">{scenarioName}</span>
          <span className="text-muted-foreground font-mono">
            (Run ID: {simulation.id.slice(0, 8)})
          </span>
        </div>
        <div className="flex items-center gap-2">
          <EpistemicBadge tier="RECOMMENDED" />
          <Link href={`/simulations/${simulation.id}`}>
            <Button size="sm" variant="outline" className="h-7 text-xs">
              Full Analysis
              <ArrowUpRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Decision Grid */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Col 1: Decision Outcome */}
        <div className="space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
            RECOMMENDED STRATEGIC DECISION
          </span>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center px-3.5 py-1.5 rounded-lg border text-sm font-extrabold tracking-wide ${decisionMeta.badgeClass}`}
            >
              {decisionMeta.label}
            </span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {rec?.executive_briefing || decisionMeta.summary}
          </p>
        </div>

        {/* Col 2: Composite Risk Score */}
        <div className="space-y-3 md:border-x md:border-border/60 md:px-6">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
              COMPOSITE RISK SCORE (CRS)
            </span>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded border ${riskMeta.badgeClass}`}
            >
              {riskMeta.label}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-black text-foreground tabular-nums">
              {crs.toFixed(1)}
            </span>
            <span className="text-xs text-muted-foreground font-mono">/ 100.0</span>
          </div>

          {/* Sub-index decomposition */}
          <div className="space-y-1.5 pt-1">
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>Logistics Strain (40%):</span>
              <span className="font-mono font-medium text-foreground">
                {(rec?.supply_chain_strain ?? 0).toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>Workforce Strain (40%):</span>
              <span className="font-mono font-medium text-foreground">
                {(rec?.workforce_strain ?? 0).toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>Demand Volatility (20%):</span>
              <span className="font-mono font-medium text-foreground">
                {(rec?.demand_strain ?? 0).toFixed(1)}
              </span>
            </div>
          </div>
        </div>

        {/* Col 3: Net Financial Consequence */}
        <div className="space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                PROJECTED PROFIT IMPACT
              </span>
              <EpistemicBadge tier="CALCULATED" showIcon={false} />
            </div>

            <div className="flex items-center gap-2 mt-2">
              {isProfitable ? (
                <TrendingUp className="h-6 w-6 text-emerald-400" />
              ) : (
                <TrendingDown className="h-6 w-6 text-rose-400" />
              )}
              <span
                className={`text-3xl font-black tabular-nums ${
                  isProfitable ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {formatCurrency(netProfit, { showSign: true, compact: true })}
              </span>
            </div>

            <div className="text-xs text-muted-foreground mt-1 tabular-nums">
              Exact Net Delta: <span className="font-mono font-semibold text-foreground">{formatCurrency(netProfit, { showSign: true })}</span>
            </div>
          </div>

          {/* Primary Vulnerability Callout */}
          {rec?.primary_vulnerability && (
            <div className="rounded-md border border-amber-800/40 bg-amber-950/20 p-2.5 flex items-start gap-2 text-xs text-amber-300">
              <ShieldAlert className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
              <div>
                <span className="font-bold">Primary Vulnerability: </span>
                <span>{rec.primary_vulnerability}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Scientific Explanation & Epistemic Lineage Drawer */}
      <ScientificExplainerSection 
        isProfitable={isProfitable}
        decisionCat={decisionCat}
        crs={crs}
        netProfit={netProfit}
      />
    </div>
  );
}

function ScientificExplainerSection({
  isProfitable,
  decisionCat,
  crs,
  netProfit,
}: {
  isProfitable: boolean;
  decisionCat: string;
  crs: number;
  netProfit: number;
}) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className="border-t border-border/60 bg-muted/20 px-6 py-2.5 text-xs">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full text-muted-foreground hover:text-foreground font-medium transition-colors py-1"
      >
        <span className="flex items-center gap-2">
          <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-primary/20 text-primary text-[10px] font-bold">?</span>
          <span>Scientific Interpretation: How are these numbers and recommendations derived?</span>
        </span>
        <span className="text-[11px] underline opacity-80">
          {isOpen ? "Hide Scientific Rationale" : "View Scientific Rationale & Lineage"}
        </span>
      </button>

      {isOpen && (
        <div className="mt-3 pt-3 border-t border-border/40 grid grid-cols-1 md:grid-cols-3 gap-4 text-muted-foreground animate-in fade-in duration-200">
          <div className="space-y-1.5 bg-background/50 p-3 rounded-lg border border-border/40">
            <span className="font-bold text-foreground text-[11px] uppercase tracking-wider block">
              1. Recommendation Rule Origin
            </span>
            <p className="text-[11px] leading-relaxed">
              Synthesized by <span className="font-mono text-primary">RecommendationEngine</span> via deterministic rules (<span className="font-mono">RULE-01 to RULE-07</span>).
              {!isProfitable ? (
                <span> Triggered <span className="font-mono text-rose-400">RULE-04 (Margin Erosion)</span>: commercial revenue expands, but downstream delay penalties and employee replacement drag produce negative operating margin.</span>
              ) : (
                <span> Commercial expansion remains within operational capacity and maintains positive operating profit.</span>
              )}
            </p>
          </div>

          <div className="space-y-1.5 bg-background/50 p-3 rounded-lg border border-border/40">
            <span className="font-bold text-foreground text-[11px] uppercase tracking-wider block">
              2. Composite Risk Score (CRS)
            </span>
            <p className="text-[11px] leading-relaxed">
              Calculated as a balanced linear combination:
              <br />
              <span className="font-mono text-foreground">CRS = 0.40(Logistics) + 0.40(Workforce) + 0.20(Demand)</span>.
              <br />
              Current score <span className="font-bold text-foreground">{crs.toFixed(1)}/100</span> reflects operational strain across logistics delivery SLA compliance and employee turnover fatigue.
            </p>
          </div>

          <div className="space-y-1.5 bg-background/50 p-3 rounded-lg border border-border/40">
            <span className="font-bold text-foreground text-[11px] uppercase tracking-wider block">
              3. Financial Calculation Formula
            </span>
            <p className="text-[11px] leading-relaxed">
              Governed by managerial accounting equations:
              <br />
              <span className="font-mono text-foreground">&Delta;&Pi; = &Delta;R_realized - (&Delta;COGS + &Delta;C_logistics + &Delta;C_workforce)</span>.
              <br />
              Employee turnover drag is calculated at <span className="font-bold text-foreground">$30,000</span> per departed employee (<span className="font-mono text-primary">ASM-004</span> benchmark).
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
