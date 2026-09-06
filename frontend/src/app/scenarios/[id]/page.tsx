"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { scenariosApi } from "@/lib/api/scenarios";
import { ScenarioLevers } from "@/lib/api/types";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Select } from "@/components/ui/select";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDate, formatPercent, formatDelta } from "@/lib/utils";
import { VALID_SHIPPING_MODES } from "@/lib/constants";
import {
  Sliders,
  Play,
  History,
  RotateCcw,
  Save,
  Check,
  AlertCircle,
  Clock,
  Layers,
} from "lucide-react";

export default function ScenarioWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const scenarioId = params.id as string;

  // Query scenario detail with versions
  const { data: scenario, isLoading, error, refetch } = useQuery({
    queryKey: ["scenario", scenarioId],
    queryFn: () => scenariosApi.getById(scenarioId),
  });

  // Local state for interactive lever modifications
  const [demandGrowth, setDemandGrowth] = React.useState(0.0);
  const [promoActive, setPromoActive] = React.useState(false);
  const [scheduledDaysOffset, setScheduledDaysOffset] = React.useState(0);
  const [shippingMode, setShippingMode] = React.useState<string>("");
  const [overtimePct, setOvertimePct] = React.useState(0.0);
  const [salaryHike, setSalaryHike] = React.useState<number | "">("");

  const [hasUnsavedChanges, setHasUnsavedChanges] = React.useState(false);
  const [saveSuccessMessage, setSaveSuccessMessage] = React.useState<string | null>(null);

  // Sync latest version into state when scenario loads
  React.useEffect(() => {
    if (scenario?.versions && scenario.versions.length > 0) {
      const latest = scenario.versions[scenario.versions.length - 1];
      setDemandGrowth(latest.demand_growth_pct);
      setPromoActive(latest.promo_active);
      setScheduledDaysOffset(latest.scheduled_days_offset);
      setShippingMode(latest.shipping_mode_override || "");
      setOvertimePct(latest.overtime_workforce_pct);
      setSalaryHike(
        latest.salary_hike_override !== null && latest.salary_hike_override !== undefined
          ? latest.salary_hike_override
          : ""
      );
      setHasUnsavedChanges(false);
    }
  }, [scenario]);

  const latestVersionNumber = scenario?.versions?.length || 1;
  const nextVersionNumber = latestVersionNumber + 1;

  // Mutation to create new immutable version
  const saveVersionMutation = useMutation({
    mutationFn: (newLevers: ScenarioLevers) =>
      scenariosApi.update(scenarioId, { new_levers: newLevers }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenario", scenarioId] });
      setHasUnsavedChanges(false);
      setSaveSuccessMessage(`New immutable version v${nextVersionNumber} saved.`);
      setTimeout(() => setSaveSuccessMessage(null), 3000);
    },
  });

  const handleSaveVersion = (e: React.FormEvent) => {
    e.preventDefault();
    const leversPayload: ScenarioLevers = {
      demand_growth_pct: demandGrowth,
      promo_active: promoActive,
      scheduled_days_offset: scheduledDaysOffset,
      shipping_mode_override: shippingMode || null,
      overtime_workforce_pct: overtimePct,
      salary_hike_override: salaryHike === "" ? null : Number(salaryHike),
    };
    saveVersionMutation.mutate(leversPayload);
  };

  const resetToBaseline = () => {
    setDemandGrowth(0.0);
    setPromoActive(false);
    setScheduledDaysOffset(0);
    setShippingMode("");
    setOvertimePct(0.0);
    setSalaryHike("");
    setHasUnsavedChanges(true);
  };

  const handleRunSimulation = () => {
    const latestVersion =
      scenario?.versions && scenario.versions.length > 0
        ? scenario.versions[scenario.versions.length - 1]
        : null;

    if (latestVersion) {
      router.push(`/simulate?scenario_id=${scenarioId}&version_id=${latestVersion.id}`);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <CardSkeleton className="h-24" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <CardSkeleton className="lg:col-span-2 h-96" />
          <CardSkeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (error || !scenario) {
    return (
      <ErrorBanner
        title="Failed to Load Scenario Workspace"
        message={(error as Error)?.message || "Scenario not found."}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={scenario.name}
        description={
          scenario.description ||
          "Interactive scenario lever workspace. Parameterize operational shocks across demand, logistics, and workforce."
        }
        epistemicNote="Levers represent ASSUMED what-if variables. Modifying levers increments the immutable version."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={resetToBaseline}
              title="Reset levers to neutral baseline values"
            >
              <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
              Reset Levers
            </Button>
            <Button size="sm" onClick={handleRunSimulation}>
              <Play className="h-3.5 w-3.5 mr-1.5" />
              Simulate Scenario
            </Button>
          </div>
        }
      />

      {/* Unsaved Changes Banner */}
      {hasUnsavedChanges && (
        <div className="rounded-lg border border-amber-800/60 bg-amber-950/40 p-3 flex items-center justify-between text-xs text-amber-200">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-400 shrink-0" />
            <span>
              You have modified levers. Saving will create immutable version{" "}
              <strong className="font-mono">v{nextVersionNumber}</strong>.
            </span>
          </div>
          <Button
            size="sm"
            onClick={handleSaveVersion}
            disabled={saveVersionMutation.isPending}
            className="h-7 text-xs bg-amber-600 hover:bg-amber-500 text-white"
          >
            <Save className="h-3 w-3 mr-1" />
            {saveVersionMutation.isPending ? "Saving..." : `Save as v${nextVersionNumber}`}
          </Button>
        </div>
      )}

      {saveSuccessMessage && (
        <div className="rounded-lg border border-emerald-800/60 bg-emerald-950/40 p-3 flex items-center gap-2 text-xs text-emerald-200">
          <Check className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>{saveSuccessMessage}</span>
        </div>
      )}

      {/* Main Two-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Interactive Levers Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base flex items-center gap-2">
                  <Sliders className="h-4 w-4 text-primary" />
                  What-If Scenario Levers
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Adjust hypothetical operational shocks within verified analytical bounds.
                </p>
              </div>
              <EpistemicBadge tier="ASSUMED" />
            </CardHeader>

            <CardContent className="space-y-6 pt-2">
              {/* Lever 1: Retail Demand Shock */}
              <div className="space-y-2 p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-xs font-semibold text-foreground">
                      Demand Growth Shock
                    </label>
                    <p className="text-[11px] text-muted-foreground">
                      Retail sales volume percentage shift [-50%, +100%]
                    </p>
                  </div>
                  <span className="font-mono font-bold text-sm text-primary tabular-nums">
                    {formatPercent(demandGrowth, { showSign: true })}
                  </span>
                </div>
                <Slider
                  value={demandGrowth}
                  min={-50}
                  max={100}
                  step={1}
                  unit="%"
                  onChange={(val) => {
                    setDemandGrowth(val);
                    setHasUnsavedChanges(true);
                  }}
                  ariaLabel="Demand Growth Shock"
                />
                <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
                  <span>-50%</span>
                  <span>0% (Baseline)</span>
                  <span>+100%</span>
                </div>
              </div>

              {/* Lever 2: Promotional Campaign Toggle */}
              <div className="flex items-center justify-between p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <div>
                  <label className="text-xs font-semibold text-foreground">
                    Promotional Campaign Activation
                  </label>
                  <p className="text-[11px] text-muted-foreground">
                    Rossmann empirical promo lift (+82.5% sales lift pattern)
                  </p>
                </div>
                <Button
                  type="button"
                  variant={promoActive ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    setPromoActive(!promoActive);
                    setHasUnsavedChanges(true);
                  }}
                  className="h-8 text-xs font-semibold cursor-pointer"
                >
                  {promoActive ? "PROMO ACTIVE" : "OFF / BASELINE"}
                </Button>
              </div>

              {/* Lever 3: Scheduled Lead Time Offset */}
              <div className="space-y-2 p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-xs font-semibold text-foreground">
                      Lead Time Scheduling Offset
                    </label>
                    <p className="text-[11px] text-muted-foreground">
                      Delivery promise schedule delta in days [-3 to +3 days]
                    </p>
                  </div>
                  <span className="font-mono font-bold text-sm text-foreground tabular-nums">
                    {formatDelta(scheduledDaysOffset, "Days", 0)}
                  </span>
                </div>
                <Slider
                  value={scheduledDaysOffset}
                  min={-3}
                  max={3}
                  step={1}
                  unit=" Days"
                  onChange={(val) => {
                    setScheduledDaysOffset(val);
                    setHasUnsavedChanges(true);
                  }}
                  ariaLabel="Lead Time Offset"
                />
                <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
                  <span>-3 Days (Aggressive)</span>
                  <span>0 Days</span>
                  <span>+3 Days (Relaxed)</span>
                </div>
              </div>

              {/* Lever 4: Shipping Mode Override */}
              <div className="space-y-2 p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <label className="text-xs font-semibold text-foreground">
                  Logistics Shipping Mode Override
                </label>
                <p className="text-[11px] text-muted-foreground">
                  Overrides standard carrier shipping mode distribution across all order batches.
                </p>
                <Select
                  value={shippingMode}
                  onChange={(e) => {
                    setShippingMode(e.target.value);
                    setHasUnsavedChanges(true);
                  }}
                >
                  <option value="">None (Preserve Benchmark Historical Distribution)</option>
                  {VALID_SHIPPING_MODES.map((mode) => (
                    <option key={mode} value={mode}>
                      {mode}
                    </option>
                  ))}
                </Select>
              </div>

              {/* Lever 5: Workforce Mandatory Overtime */}
              <div className="space-y-2 p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-xs font-semibold text-foreground">
                      Workforce Overtime Coverage
                    </label>
                    <p className="text-[11px] text-muted-foreground">
                      Target percentage of workforce operating with mandatory overtime [0%, 100%]
                    </p>
                  </div>
                  <span className="font-mono font-bold text-sm text-amber-400 tabular-nums">
                    {formatPercent(overtimePct)}
                  </span>
                </div>
                <Slider
                  value={overtimePct}
                  min={0}
                  max={100}
                  step={1}
                  unit="%"
                  onChange={(val) => {
                    setOvertimePct(val);
                    setHasUnsavedChanges(true);
                  }}
                  ariaLabel="Overtime Coverage"
                />
                <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
                  <span>0% (No Mandatory OT)</span>
                  <span>50%</span>
                  <span>100% (Full OT)</span>
                </div>
              </div>

              {/* Lever 6: Salary Hike Override */}
              <div className="space-y-2 p-3.5 rounded-lg border border-border/60 bg-muted/20">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-xs font-semibold text-foreground">
                      Compensation Hike Override
                    </label>
                    <p className="text-[11px] text-muted-foreground">
                      Optional retention incentive wage hike [0%, 50%]
                    </p>
                  </div>
                  <span className="font-mono font-bold text-sm text-emerald-400 tabular-nums">
                    {salaryHike === "" ? "None" : `+${salaryHike}%`}
                  </span>
                </div>
                <Slider
                  value={salaryHike === "" ? 0 : Number(salaryHike)}
                  min={0}
                  max={50}
                  step={1}
                  unit="%"
                  onChange={(val) => {
                    setSalaryHike(val === 0 ? "" : val);
                    setHasUnsavedChanges(true);
                  }}
                  ariaLabel="Salary Hike Override"
                />
              </div>

              {/* Save Version Action */}
              <div className="flex justify-end pt-4 border-t border-border/50">
                <Button
                  onClick={handleSaveVersion}
                  disabled={!hasUnsavedChanges || saveVersionMutation.isPending}
                >
                  <Save className="h-4 w-4 mr-1.5" />
                  {saveVersionMutation.isPending
                    ? "Persisting..."
                    : `Persist Levers as Version v${nextVersionNumber}`}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Version History & Immutability Audit */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <History className="h-4 w-4 text-primary" />
                Version History (Gate G)
              </CardTitle>
              <p className="text-xs text-muted-foreground">
                Immutable snapshots guaranteed by database constraints.
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              {scenario.versions?.map((ver) => (
                <div
                  key={ver.id}
                  className={`p-3 rounded-md border text-xs space-y-2 ${
                    ver.version_number === latestVersionNumber
                      ? "border-primary/50 bg-primary/5"
                      : "border-border/60 bg-muted/20"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-foreground">
                      Version v{ver.version_number}
                    </span>
                    {ver.version_number === latestVersionNumber && (
                      <span className="rounded bg-primary/20 text-primary px-1.5 py-0.5 text-[10px] font-bold">
                        ACTIVE LATEST
                      </span>
                    )}
                  </div>

                  <div className="space-y-1 text-[11px] text-muted-foreground">
                    <div className="flex justify-between">
                      <span>Demand Shock:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatPercent(ver.demand_growth_pct, { showSign: true })}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Overtime Workforce:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatPercent(ver.overtime_workforce_pct)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Lead Time Offset:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatDelta(ver.scheduled_days_offset, "d", 0)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-1 border-t border-border/40 font-mono">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatDate(ver.created_at)}
                    </span>
                    <Link
                      href={`/simulate?scenario_id=${scenarioId}&version_id=${ver.id}`}
                      className="text-primary hover:underline font-bold"
                    >
                      Simulate &rarr;
                    </Link>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Academic Governance Callout */}
          <div className="rounded-lg border border-border bg-card/60 p-4 text-xs text-muted-foreground space-y-2">
            <h5 className="font-semibold text-foreground flex items-center gap-1.5">
              <Layers className="h-3.5 w-3.5 text-primary" />
              Epistemic Guarantee
            </h5>
            <p className="leading-relaxed">
              In accordance with Section 13.3 of <code className="text-foreground">AGENTS.md</code>, what-if parameters do not alter historical data records. Every simulation run seals an 8-element cryptographic tuple guaranteeing reproducible experimental results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
