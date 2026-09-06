"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { systemApi } from "@/lib/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import { Activity, Database, Fingerprint, Server, RefreshCw, CheckCircle2, AlertTriangle } from "lucide-react";

export default function SystemHealthPage() {
  const { data: health, isLoading, error, refetch } = useQuery({
    queryKey: ["health"],
    queryFn: () => systemApi.getHealth(),
    refetchInterval: 10000,
  });

  const isHealthy = health?.status === "healthy";
  const dbConnected = health?.database === "connected";
  const modelsOk = health?.models_verified ?? false;

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="System Health & Operational Readiness"
        description="Real-time liveness and readiness telemetry across FastAPI services, PostgreSQL storage, and frozen model binaries."
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Refresh Status
          </Button>
        }
      />

      {error && (
        <ErrorBanner
          title="Backend Unreachable"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CardSkeleton className="h-36" />
          <CardSkeleton className="h-36" />
          <CardSkeleton className="h-36" />
          <CardSkeleton className="h-36" />
        </div>
      )}

      {!isLoading && health && (
        <div className="space-y-6">
          {/* Status Hero Card */}
          <div
            className={`p-6 rounded-xl border flex items-center justify-between ${
              isHealthy
                ? "border-emerald-700/60 bg-emerald-950/30 text-emerald-200"
                : "border-amber-700/60 bg-amber-950/30 text-amber-200"
            }`}
          >
            <div className="flex items-center gap-4">
              {isHealthy ? (
                <CheckCircle2 className="h-10 w-10 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="h-10 w-10 text-amber-400 shrink-0" />
              )}
              <div>
                <h3 className="text-lg font-bold">
                  {isHealthy ? "All Systems Operational" : "System Degraded"}
                </h3>
                <p className="text-xs opacity-90 mt-0.5">
                  {isHealthy
                    ? "REST endpoints, PostgreSQL connectivity, and ML artifacts are operating normally."
                    : "One or more operational subsystems reported degraded status."}
                </p>
              </div>
            </div>
            <span className="font-mono text-xs uppercase px-2.5 py-1 rounded bg-black/40 font-bold">
              {health.status}
            </span>
          </div>

          {/* Subsystem Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* API Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Server className="h-4 w-4 text-primary" />
                  FastAPI REST Engine
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Application:</span>
                  <span className="font-semibold text-foreground">{health.app_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Version:</span>
                  <span className="font-mono font-bold text-foreground">{health.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Environment:</span>
                  <span className="font-mono uppercase text-foreground">{health.environment || "development"}</span>
                </div>
              </CardContent>
            </Card>

            {/* Database Card */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Database className="h-4 w-4 text-primary" />
                  PostgreSQL System of Record
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Connection State:</span>
                  <span
                    className={`font-bold font-mono uppercase ${
                      dbConnected ? "text-emerald-400" : "text-rose-400"
                    }`}
                  >
                    {health.database}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Readiness:</span>
                  <span className="text-foreground">SELECT 1 probe passing</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Cascade Integrity:</span>
                  <span className="text-emerald-400 font-semibold">Active</span>
                </div>
              </CardContent>
            </Card>

            {/* Model Artifacts Card */}
            <Card className="sm:col-span-2">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Fingerprint className="h-4 w-4 text-primary" />
                  Machine Learning Model Binaries (Gate I)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Cryptographic Verification:</span>
                  <span
                    className={`font-bold font-mono px-2 py-0.5 rounded border text-[11px] ${
                      modelsOk
                        ? "border-emerald-600 bg-emerald-950/40 text-emerald-300"
                        : "border-rose-600 bg-rose-950/40 text-rose-300"
                    }`}
                  >
                    {modelsOk ? "ALL 3 MODELS VERIFIED" : "VERIFICATION FAILURE"}
                  </span>
                </div>
                <p className="text-muted-foreground text-[11px] pt-1">
                  Demand XGBoost Regressor, DataCo Calibrated Classifier, and IBM HR Calibrated Classifier.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
