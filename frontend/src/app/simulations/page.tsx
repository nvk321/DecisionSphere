"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { simulationsApi } from "@/lib/api/simulations";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDate, formatCurrency } from "@/lib/utils";
import { History, Play, ArrowRight, Layers, CheckCircle2 } from "lucide-react";

export default function SimulationRunsPage() {
  const [page, setPage] = React.useState(0);
  const limit = 20;

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["simulations", page],
    queryFn: () => simulationsApi.list({ skip: page * limit, limit }),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Simulation Run History"
        description="Chronological registry of multi-domain simulation executions, managerial accounting outcomes, and audit records."
        epistemicNote="Each simulation run seals an immutable cryptographic audit record."
        actions={
          <Link href="/simulate">
            <Button size="sm">
              <Play className="h-4 w-4 mr-1.5" />
              New Simulation
            </Button>
          </Link>
        }
      />

      {error && (
        <ErrorBanner
          title="Failed to Load Simulation History"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {isLoading && <TableSkeleton rows={8} />}

      {!isLoading && data?.items && data.items.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <History className="h-4 w-4 text-primary" />
              Executed Decision Runs ({data.total} Total)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Execution Time</TableHead>
                  <TableHead>Decision Category</TableHead>
                  <TableHead>Composite Risk Score</TableHead>
                  <TableHead>Net Profit Impact</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((run) => {
                  const isProfitable = (run.net_profit_delta ?? 0) >= 0;

                  return (
                    <TableRow key={run.id}>
                      <TableCell className="font-mono text-xs font-semibold text-foreground">
                        <Link
                          href={`/simulations/${run.id}`}
                          className="hover:underline flex items-center gap-1.5"
                        >
                          <Layers className="h-3.5 w-3.5 text-primary" />
                          <span>{run.id.slice(0, 8)}...</span>
                        </Link>
                      </TableCell>

                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {formatDate(run.executed_at)}
                      </TableCell>

                      <TableCell>
                        <span className="text-xs font-bold tracking-wide">
                          {run.decision_category || "COMPLETED"}
                        </span>
                      </TableCell>

                      <TableCell className="font-mono text-xs tabular-nums">
                        {run.composite_risk_score !== null && run.composite_risk_score !== undefined
                          ? run.composite_risk_score.toFixed(1)
                          : "—"}
                      </TableCell>

                      <TableCell
                        className={`font-mono text-xs tabular-nums font-semibold ${
                          isProfitable ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {run.net_profit_delta !== null && run.net_profit_delta !== undefined
                          ? formatCurrency(run.net_profit_delta, { showSign: true, compact: true })
                          : "—"}
                      </TableCell>

                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {run.execution_duration_ms
                          ? `${run.execution_duration_ms.toFixed(0)} ms`
                          : "—"}
                      </TableCell>

                      <TableCell className="text-right">
                        <Link href={`/simulations/${run.id}`}>
                          <Button size="sm" variant="outline" className="h-8 text-xs">
                            View Result
                            <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {!isLoading && (!data?.items || data.items.length === 0) && (
        <EmptyState
          icon={<History className="h-8 w-8 text-primary" />}
          title="No Simulation Runs Yet"
          description="Execute a simulation from the Scenario Workspace to generate multi-domain risk evaluation records."
          actionLabel="Run Simulation"
          onAction={() => {
            window.location.href = "/simulate";
          }}
        />
      )}
    </div>
  );
}
