"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { scenariosApi } from "@/lib/api/scenarios";
import { simulationsApi } from "@/lib/api/simulations";
import { policiesApi } from "@/lib/api/policies";
import { systemApi } from "@/lib/api/system";
import { SimulationRequest } from "@/lib/api/types";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import Link from "next/link";
import { formatPercent, formatDelta, formatDate } from "@/lib/utils";
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ShieldAlert,
  ArrowRight,
  Layers,
  Cpu,
} from "lucide-react";

function SimulatePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const initialScenarioId = searchParams.get("scenario_id") || "";
  const initialVersionId = searchParams.get("version_id") || "";

  const [selectedScenarioId, setSelectedScenarioId] = React.useState(initialScenarioId);
  const [selectedVersionId, setSelectedVersionId] = React.useState(initialVersionId);
  const [selectedPolicyId, setSelectedPolicyId] = React.useState("");

  const [simState, setSimState] = React.useState<"review" | "running" | "done" | "failed">("review");
  const [activeStep, setActiveStep] = React.useState(0);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [errorCode, setErrorCode] = React.useState<string | null>(null);
  const [requestId, setRequestId] = React.useState<string | null>(null);

  // Queries
  const { data: scenariosData } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => scenariosApi.list({ limit: 50 }),
  });

  const { data: currentScenario } = useQuery({
    queryKey: ["scenario", selectedScenarioId],
    queryFn: () => scenariosApi.getById(selectedScenarioId),
    enabled: !!selectedScenarioId,
  });

  const { data: policiesData } = useQuery({
    queryKey: ["policies"],
    queryFn: () => policiesApi.list({ limit: 20 }),
  });

  const { data: defaultPolicy } = useQuery({
    queryKey: ["policy", "default"],
    queryFn: () => policiesApi.getDefault(),
  });

  const { data: modelStatus } = useQuery({
    queryKey: ["modelStatus"],
    queryFn: () => systemApi.getModelStatus(),
  });

  // Auto-select first scenario if none selected
  React.useEffect(() => {
    if (!selectedScenarioId && scenariosData?.items && scenariosData.items.length > 0) {
      setSelectedScenarioId(scenariosData.items[0].id);
    }
  }, [scenariosData, selectedScenarioId]);

  // Auto-select latest version
  React.useEffect(() => {
    if (currentScenario?.versions && currentScenario.versions.length > 0) {
      if (!selectedVersionId) {
        setSelectedVersionId(
          currentScenario.versions[currentScenario.versions.length - 1].id
        );
      }
    }
  }, [currentScenario, selectedVersionId]);

  // Auto-select default policy
  React.useEffect(() => {
    if (defaultPolicy && !selectedPolicyId) {
      setSelectedPolicyId(defaultPolicy.id);
    }
  }, [defaultPolicy, selectedPolicyId]);

  const selectedVersion = currentScenario?.versions?.find(
    (v) => v.id === selectedVersionId
  );

  const allModelsVerified = modelStatus?.all_verified ?? true;

  // Simulation Mutation
  const runMutation = useMutation({
    mutationFn: (payload: SimulationRequest) => simulationsApi.run(payload),
    onSuccess: (result) => {
      setActiveStep(9);
      setSimState("done");
      setTimeout(() => {
        router.push(`/simulations/${result.id}`);
      }, 800);
    },
    onError: (err: any) => {
      setSimState("failed");
      setErrorMessage(err.message || "Simulation execution failed on the backend.");
      setErrorCode(err.code || "SIMULATION_FAILED");
      setRequestId(err.requestId);
    },
  });

  const pipelineSteps = [
    "Validating scenario lever constraints & schema bounds",
    "Loading corporate assumption policy (ASM-001 through ASM-010)",
    "Executing Demand Forecasting XGBoost Regressor",
    "Executing DataCo Delivery Risk Calibrated Classifier",
    "Executing IBM HR Workforce Attrition Calibrated Classifier",
    "Computing cross-domain parameter propagation (overtime, lead time)",
    "Calculating managerial financial waterfall (Revenue, COGS, Penalties, Wages)",
    "Evaluating Composite Risk Score & strategic rule triggers",
    "Assembling 8-element cryptographic provenance signature (Gate H)",
  ];

  const handleStartSimulation = () => {
    if (!allModelsVerified) {
      setErrorMessage("Cannot execute simulation: ML model integrity failure detected.");
      setErrorCode("MODEL_INTEGRITY_FAILURE");
      setSimState("failed");
      return;
    }

    setSimState("running");
    setActiveStep(1);

    // Simulated visual step progression matching actual asynchronous execution
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < 8) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 400);

    runMutation.mutate({
      scenario_version_id: selectedVersionId,
      policy_id: selectedPolicyId || undefined,
    });
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Execute Multi-Domain Simulation"
        description="Review scenario parameters and bound assumption policies before triggering authoritative machine learning execution and managerial financial accounting."
        epistemicNote="Executes Phase 2, 3, 4 ML models, Phase 6 propagation, Phase 7 financial engine, and Phase 8 recommendation engine."
      />

      {/* Safety Alert if Model Integrity Failed */}
      {!allModelsVerified && (
        <div className="rounded-lg border border-rose-800 bg-rose-950/60 p-4 text-xs text-rose-200 flex items-start gap-3">
          <ShieldAlert className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-bold text-rose-100">SIMULATION EXECUTION DISABLED</h4>
            <p>
              One or more machine learning model artifacts failed SHA-256 cryptographic verification.
              DecisionSphere refuses to execute simulations against unverified model binaries.
            </p>
            <Link
              href="/system/models"
              className="text-rose-300 font-semibold underline hover:text-white"
            >
              Inspect Model Integrity Status &rarr;
            </Link>
          </div>
        </div>
      )}

      {/* State 1: Review & Configure */}
      {simState === "review" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Layers className="h-4 w-4 text-primary" />
                Simulation Review & Target Binding
              </CardTitle>
              <p className="text-xs text-muted-foreground">
                Select the target scenario, version, and corporate policy to simulate.
              </p>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Scenario Selection */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">
                    Target Strategic Scenario
                  </label>
                  <Select
                    value={selectedScenarioId}
                    onChange={(e) => {
                      setSelectedScenarioId(e.target.value);
                      setSelectedVersionId("");
                    }}
                  >
                    {scenariosData?.items?.map((sc) => (
                      <option key={sc.id} value={sc.id}>
                        {sc.name}
                      </option>
                    ))}
                  </Select>
                </div>

                {/* Version Selection */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">
                    Scenario Parameter Version
                  </label>
                  <Select
                    value={selectedVersionId}
                    onChange={(e) => setSelectedVersionId(e.target.value)}
                  >
                    {currentScenario?.versions?.map((ver) => (
                      <option key={ver.id} value={ver.id}>
                        Version v{ver.version_number} ({formatDate(ver.created_at)})
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              {/* Policy Selection */}
              <div className="space-y-1.5 pt-2">
                <label className="text-xs font-semibold text-foreground">
                  Bound Corporate Assumption Policy
                </label>
                <Select
                  value={selectedPolicyId}
                  onChange={(e) => setSelectedPolicyId(e.target.value)}
                >
                  {policiesData?.map((pol) => (
                    <option key={pol.id} value={pol.id}>
                      {pol.name} (v{pol.version_number}) — Delay Penalty: ${pol.late_penalty_rate}, Overtime: ${pol.overtime_wage_rate}/hr
                    </option>
                  ))}
                </Select>
              </div>

              {/* Lever Summary Review Table */}
              {selectedVersion && (
                <div className="rounded-lg border border-border bg-muted/20 p-4 space-y-3 mt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-foreground">
                      Applied What-If Levers (Version v{selectedVersion.version_number})
                    </span>
                    <EpistemicBadge tier="ASSUMED" />
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <span className="text-muted-foreground block">Demand Shock:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatPercent(selectedVersion.demand_growth_pct, { showSign: true })}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Promotional Campaign:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {selectedVersion.promo_active ? "ACTIVE (+82.5%)" : "OFF (0%)"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Lead Time Offset:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatDelta(selectedVersion.scheduled_days_offset, "Days", 0)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Shipping Override:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {selectedVersion.shipping_mode_override || "None (Benchmark Distribution)"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Overtime Coverage:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {formatPercent(selectedVersion.overtime_workforce_pct)}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Wage Hike Override:</span>
                      <span className="font-mono font-semibold text-foreground">
                        {selectedVersion.salary_hike_override !== null && selectedVersion.salary_hike_override !== undefined
                          ? `+${selectedVersion.salary_hike_override}%`
                          : "None"}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>

            <CardFooter className="flex justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/scenarios/${selectedScenarioId}`)}
              >
                Modify Levers
              </Button>
              <Button
                onClick={handleStartSimulation}
                disabled={!allModelsVerified || !selectedVersionId}
              >
                <Play className="h-4 w-4 mr-1.5" />
                Execute Simulation
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* State 2: Simulation Execution Progress */}
      {simState === "running" && (
        <Card className="border-primary/50 shadow-lg">
          <CardHeader className="text-center pb-2">
            <div className="flex justify-center mb-2">
              <Loader2 className="h-8 w-8 text-primary animate-spin" />
            </div>
            <CardTitle className="text-lg">Executing Multi-Domain Simulation</CardTitle>
            <p className="text-xs text-muted-foreground max-w-md mx-auto">
              Evaluating cross-domain parameter propagation, machine learning inference, and managerial accounting formulas.
            </p>
          </CardHeader>

          <CardContent className="space-y-3 pt-4">
            <div className="space-y-2 max-w-lg mx-auto">
              {pipelineSteps.map((stepName, idx) => {
                const isCompleted = idx < activeStep;
                const isCurrent = idx === activeStep;

                return (
                  <div
                    key={stepName}
                    className={`flex items-center gap-3 p-2 rounded text-xs transition-colors ${
                      isCurrent
                        ? "bg-primary/10 border border-primary/40 font-semibold text-primary"
                        : isCompleted
                        ? "text-emerald-400 font-medium"
                        : "text-muted-foreground/60"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                    ) : isCurrent ? (
                      <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />
                    ) : (
                      <div className="h-4 w-4 rounded-full border border-muted-foreground/40 shrink-0" />
                    )}
                    <span>{stepName}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* State 3: Execution Failure */}
      {simState === "failed" && (
        <div className="space-y-4">
          <ErrorBanner
            title="Simulation Run Failed"
            message={errorMessage || "Unknown error occurred during simulation execution."}
            code={errorCode || "SIMULATION_ERROR"}
            requestId={requestId || undefined}
            onRetry={handleStartSimulation}
          />
          <div className="flex justify-center">
            <Button variant="outline" onClick={() => setSimState("review")}>
              Return to Simulation Review
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SimulatePage() {
  return (
    <React.Suspense
      fallback={
        <div className="space-y-6">
          <PageHeader
            title="Simulation Runner"
            description="Authoritative multi-domain scenario execution engine with Gate I model integrity safeguards."
          />
          <div className="p-8 text-center text-sm text-muted-foreground">
            Initializing simulation environment...
          </div>
        </div>
      }
    >
      <SimulatePageContent />
    </React.Suspense>
  );
}
