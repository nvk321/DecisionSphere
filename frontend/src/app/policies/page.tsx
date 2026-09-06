"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { policiesApi } from "@/lib/api/policies";
import { PolicyCreate } from "@/lib/api/types";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDate, formatPercent, formatCurrency } from "@/lib/utils";
import { ShieldCheck, Plus, CheckCircle2, AlertCircle, Info, Scale } from "lucide-react";

export default function PoliciesPage() {
  const queryClient = useQueryClient();
  const [createModalOpen, setCreateModalOpen] = React.useState(false);
  const [formError, setFormError] = React.useState<string | null>(null);

  // Form State
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [latePenalty, setLatePenalty] = React.useState(25.0);
  const [expediteFee, setExpediteFee] = React.useState(15.0);
  const [churnFactor, setChurnFactor] = React.useState(0.15);
  const [replacementCost, setReplacementCost] = React.useState(30000.0);
  const [overtimeRate, setOvertimeRate] = React.useState(45.0);
  const [cogsRatio, setCogsRatio] = React.useState(0.60);
  const [wSupply, setWSupply] = React.useState(0.40);
  const [wWorkforce, setWWorkforce] = React.useState(0.40);
  const [wDemand, setWDemand] = React.useState(0.20);
  const [tauRisk, setTauRisk] = React.useState(50.0);

  const { data: policies, isLoading, error, refetch } = useQuery({
    queryKey: ["policies"],
    queryFn: () => policiesApi.list({ limit: 50 }),
  });

  const simplexSum = Math.round((wSupply + wWorkforce + wDemand) * 100) / 100;
  const isSimplexValid = Math.abs(simplexSum - 1.0) < 0.001;

  const createMutation = useMutation({
    mutationFn: (payload: PolicyCreate) => policiesApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policies"] });
      setCreateModalOpen(false);
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.message || "Failed to create policy version.");
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isSimplexValid) {
      setFormError(`CRS domain weights must sum to exactly 1.0 (currently ${simplexSum}).`);
      return;
    }
    if (!name.trim()) {
      setFormError("Policy name is required.");
      return;
    }

    createMutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      late_penalty_rate: latePenalty,
      expedite_fee: expediteFee,
      stockout_churn_factor: churnFactor,
      replacement_cost: replacementCost,
      overtime_wage_rate: overtimeRate,
      cogs_ratio: cogsRatio,
      crs_w_supply: wSupply,
      crs_w_workforce: wWorkforce,
      crs_w_demand: wDemand,
      tau_risk: tauRisk,
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Corporate Assumption Policy Governance"
        description="Versioned corporate financial coupling rates (ASM-001 to ASM-005) and multi-criteria risk weighting simplexes (ASM-009, ASM-010)."
        epistemicNote="Policies govern deterministic financial accounting formulas and Composite Risk Score triggers."
        actions={
          <Button onClick={() => setCreateModalOpen(true)}>
            <Plus className="h-4 w-4 mr-1.5" />
            New Policy Version
          </Button>
        }
      />

      {error && (
        <ErrorBanner
          title="Failed to Load Assumption Policies"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {isLoading && <TableSkeleton rows={4} />}

      {!isLoading && policies && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-primary" />
              Corporate Assumption Policies ({policies.length} Versions)
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Creating a new policy version creates an immutable snapshot; existing simulation runs remain locked to their historical policy.
            </p>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Policy Name & Version</TableHead>
                  <TableHead>Simplex Weights (SC, WF, Demand)</TableHead>
                  <TableHead>Penalty (ASM-001)</TableHead>
                  <TableHead>Overtime Wage (ASM-005)</TableHead>
                  <TableHead>Turnover Cost (ASM-004)</TableHead>
                  <TableHead>Risk Threshold</TableHead>
                  <TableHead className="text-right">Effective Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {policies.map((policy) => (
                  <TableRow key={policy.id}>
                    <TableCell>
                      <div className="font-semibold text-xs text-foreground flex items-center gap-2">
                        <span>{policy.name}</span>
                        <span className="rounded bg-primary/20 text-primary px-1.5 py-0.5 font-mono text-[10px] font-bold">
                          v{policy.version_number}
                        </span>
                        {policy.version_number === 1 && (
                          <span className="rounded bg-emerald-950 text-emerald-400 border border-emerald-700/60 px-1.5 py-0.2 text-[9px] font-bold">
                            BASELINE
                          </span>
                        )}
                      </div>
                      {policy.description && (
                        <p className="text-xs text-muted-foreground truncate max-w-xs mt-0.5">
                          {policy.description}
                        </p>
                      )}
                    </TableCell>

                    <TableCell className="font-mono text-xs">
                      {formatPercent(policy.crs_w_supply, { isRatio: true })} /{" "}
                      {formatPercent(policy.crs_w_workforce, { isRatio: true })} /{" "}
                      {formatPercent(policy.crs_w_demand, { isRatio: true })}
                    </TableCell>

                    <TableCell className="font-mono text-xs tabular-nums">
                      ${policy.late_penalty_rate.toFixed(2)}/order
                    </TableCell>

                    <TableCell className="font-mono text-xs tabular-nums">
                      ${policy.overtime_wage_rate.toFixed(2)}/hr
                    </TableCell>

                    <TableCell className="font-mono text-xs tabular-nums">
                      ${policy.replacement_cost.toLocaleString()}
                    </TableCell>

                    <TableCell className="font-mono text-xs">
                      &tau; = {policy.tau_risk}
                    </TableCell>

                    <TableCell className="text-right font-mono text-xs text-muted-foreground">
                      {formatDate(policy.created_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Creation Modal */}
      <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
        <DialogContent onClose={() => setCreateModalOpen(false)} className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Assumption Policy Version</DialogTitle>
            <DialogDescription>
              Configure corporate financial rates and multi-criteria risk simplex weights. This record is immutable once persisted.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateSubmit} className="space-y-4 max-h-[75vh] overflow-y-auto pr-2">
            {formError && (
              <div className="rounded-md border border-rose-800 bg-rose-950/60 p-3 text-xs text-rose-200">
                {formError}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Policy Title *</label>
                <Input
                  placeholder="e.g. Corporate Baseline FY2027"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">
                  Operational Strain Tolerance (&tau;<sub>risk</sub>)
                </label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  value={tauRisk}
                  onChange={(e) => setTauRisk(Number(e.target.value))}
                />
              </div>
            </div>

            {/* Simplex Weights Section */}
            <div className="rounded-lg border border-border bg-muted/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
                  <Scale className="h-4 w-4 text-primary" />
                  CRS Simplex Weights (Must sum to 1.0)
                </span>
                <span
                  className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
                    isSimplexValid
                      ? "border-emerald-600 bg-emerald-950/40 text-emerald-300"
                      : "border-rose-600 bg-rose-950/40 text-rose-300"
                  }`}
                >
                  Sum: {simplexSum.toFixed(2)} / 1.00
                </span>
              </div>

              <div className="space-y-3 pt-1">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>Supply Chain Strain Weight (w_supply):</span>
                    <span className="font-mono font-semibold">{wSupply.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={wSupply}
                    min={0}
                    max={1}
                    step={0.05}
                    onChange={(val) => setWSupply(Math.round(val * 100) / 100)}
                    ariaLabel="w_supply"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>Workforce Strain Weight (w_workforce):</span>
                    <span className="font-mono font-semibold">{wWorkforce.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={wWorkforce}
                    min={0}
                    max={1}
                    step={0.05}
                    onChange={(val) => setWWorkforce(Math.round(val * 100) / 100)}
                    ariaLabel="w_workforce"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>Demand Volatility Weight (w_demand):</span>
                    <span className="font-mono font-semibold">{wDemand.toFixed(2)}</span>
                  </div>
                  <Slider
                    value={wDemand}
                    min={0}
                    max={1}
                    step={0.05}
                    onChange={(val) => setWDemand(Math.round(val * 100) / 100)}
                    ariaLabel="w_demand"
                  />
                </div>
              </div>
            </div>

            {/* Financial Coupling Rates */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="space-y-1">
                <label className="text-muted-foreground">Late Delivery Penalty ($/order):</label>
                <Input
                  type="number"
                  min="0"
                  step="1"
                  value={latePenalty}
                  onChange={(e) => setLatePenalty(Number(e.target.value))}
                />
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">Expedite Freight Surcharge ($/order):</label>
                <Input
                  type="number"
                  min="0"
                  step="1"
                  value={expediteFee}
                  onChange={(e) => setExpediteFee(Number(e.target.value))}
                />
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">Turnover Replacement Cost ($/worker):</label>
                <Input
                  type="number"
                  min="0"
                  step="500"
                  value={replacementCost}
                  onChange={(e) => setReplacementCost(Number(e.target.value))}
                />
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">Overtime Hourly Labor Wage ($/hr):</label>
                <Input
                  type="number"
                  min="0"
                  step="1"
                  value={overtimeRate}
                  onChange={(e) => setOvertimeRate(Number(e.target.value))}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!isSimplexValid || createMutation.isPending}
              >
                {createMutation.isPending ? "Creating..." : "Persist Policy Version"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
