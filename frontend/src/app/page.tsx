"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { simulationsApi } from "@/lib/api/simulations";
import { scenariosApi } from "@/lib/api/scenarios";
import { DecisionHero } from "@/components/dashboard/DecisionHero";
import { DomainMiniMatrix } from "@/components/dashboard/DomainMiniMatrix";
import { CompactWaterfall } from "@/components/dashboard/CompactWaterfall";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { CardSkeleton, TableSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDate, formatCurrency } from "@/lib/utils";
import { PlusCircle, Play, ArrowRight, Sliders, History } from "lucide-react";

export default function DashboardPage() {
  // Query recent simulation runs
  const {
    data: runsData,
    isLoading: runsLoading,
    error: runsError,
    refetch: refetchRuns,
  } = useQuery({
    queryKey: ["simulations", "recent"],
    queryFn: () => simulationsApi.list({ limit: 5 }),
  });

  // Query scenarios count
  const { data: scenariosData, isLoading: scenariosLoading } = useQuery({
    queryKey: ["scenarios", "list"],
    queryFn: () => scenariosApi.list({ limit: 5 }),
  });

  // Get ID of the latest simulation
  const latestRunSummary = runsData?.items?.[0];

  // Fetch full details of the latest simulation run
  const {
    data: latestRunDetail,
    isLoading: detailLoading,
    error: detailError,
  } = useQuery({
    queryKey: ["simulation", latestRunSummary?.id],
    queryFn: () => simulationsApi.getById(latestRunSummary!.id),
    enabled: !!latestRunSummary?.id,
  });

  const isLoading = runsLoading || (!!latestRunSummary?.id && detailLoading);

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border/60">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            Executive Decision Cockpit
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Simulate cross-domain operational shocks, inspect managerial waterfalls, and evaluate rule-grounded strategic recommendations.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <Link href="/scenarios">
            <Button variant="outline" size="sm">
              <Sliders className="h-4 w-4 mr-1.5" />
              Scenarios
            </Button>
          </Link>
          <Link href="/simulate">
            <Button size="sm">
              <Play className="h-4 w-4 mr-1.5" />
              New Simulation
            </Button>
          </Link>
        </div>
      </div>

      {/* Error handling */}
      {(runsError || detailError) && (
        <ErrorBanner
          title="Failed to Load Dashboard Metrics"
          message={
            (runsError as Error)?.message ||
            (detailError as Error)?.message ||
            "Unable to connect to DecisionSphere API."
          }
          onRetry={() => refetchRuns()}
        />
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-6">
          <CardSkeleton className="h-64" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CardSkeleton className="h-32" />
            <CardSkeleton className="h-32" />
            <CardSkeleton className="h-32" />
          </div>
        </div>
      )}

      {/* Content: Active Simulation Run */}
      {!isLoading && latestRunDetail && (
        <div className="space-y-6">
          {/* Decision Hero */}
          <DecisionHero simulation={latestRunDetail} />

          {/* 3-Domain Mini Matrix */}
          <DomainMiniMatrix predictions={latestRunDetail.domain_predictions || []} />

          {/* 2-Column Split: Financial Waterfall & Recent Runs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Financial Waterfall Preview */}
            {latestRunDetail.financial_result && (
              <CompactWaterfall financialResult={latestRunDetail.financial_result} />
            )}

            {/* Recent Simulation Runs List */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <div className="space-y-0.5">
                  <CardTitle className="text-base flex items-center gap-2">
                    <History className="h-4 w-4 text-primary" />
                    Recent Strategic Runs
                  </CardTitle>
                  <p className="text-xs text-muted-foreground">
                    Historical multi-domain simulations and categorical recommendations.
                  </p>
                </div>
                <Link href="/simulations">
                  <Button variant="ghost" size="sm" className="text-xs h-7">
                    View All
                    <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Execution Time</TableHead>
                      <TableHead>Decision</TableHead>
                      <TableHead>CRS</TableHead>
                      <TableHead className="text-right">Profit Delta</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {runsData?.items?.map((run) => (
                      <TableRow key={run.id}>
                        <TableCell className="text-xs font-mono">
                          <Link
                            href={`/simulations/${run.id}`}
                            className="hover:underline text-foreground"
                          >
                            {formatDate(run.executed_at)}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <span className="text-[11px] font-bold">
                            {run.decision_category || "COMPLETED"}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-xs tabular-nums">
                          {run.composite_risk_score !== null && run.composite_risk_score !== undefined
                            ? run.composite_risk_score.toFixed(1)
                            : "N/A"}
                        </TableCell>
                        <TableCell className="text-right font-mono text-xs tabular-nums">
                          {run.net_profit_delta !== null && run.net_profit_delta !== undefined
                            ? formatCurrency(run.net_profit_delta, { showSign: true, compact: true })
                            : "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Empty State: No Simulation Runs Executed Yet */}
      {!isLoading && !latestRunDetail && (
        <EmptyState
          icon={<Sliders className="h-8 w-8 text-primary" />}
          title="No Strategic Simulations Executed Yet"
          description="Create a business scenario, parameterize what-if shocks, and execute a multi-domain simulation to generate evidence-backed recommendations and financial waterfalls."
          actionLabel="Create First Scenario"
          onAction={() => {
            window.location.href = "/scenarios";
          }}
        />
      )}
    </div>
  );
}
