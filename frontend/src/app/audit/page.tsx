"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { simulationsApi } from "@/lib/api/simulations";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDate, truncateId, copyToClipboard } from "@/lib/utils";
import { FileText, Copy, Check, ArrowRight, ShieldCheck, Layers, GitBranch, Database } from "lucide-react";

export default function AuditPage() {
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const { data: runsData, isLoading, error, refetch } = useQuery({
    queryKey: ["audit", "runs"],
    queryFn: () => simulationsApi.list({ limit: 50 }),
  });

  const handleCopy = async (text: string, id: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit & Provenance Explorer"
        description="Scientific audit trail and cryptographic provenance tuples (Gate H) guaranteeing strict reproducibility of all simulated decisions."
        epistemicNote="Every simulation run is sealed with an immutable 8-element cryptographic tuple (Sigma_run)."
      />

      {error && (
        <ErrorBanner
          title="Failed to Load Audit Records"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {isLoading && <TableSkeleton rows={8} />}

      {!isLoading && runsData?.items && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              Cryptographic Execution Signatures ({runsData.total} Runs)
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Select any execution run to inspect its model hashes, Git commit, runtime environment, and relational tree.
            </p>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Simulation Run ID</TableHead>
                  <TableHead>Scenario Version</TableHead>
                  <TableHead>Bound Policy</TableHead>
                  <TableHead>Execution Timestamp</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runsData.items.map((run) => (
                  <TableRow key={run.id}>
                    <TableCell className="font-mono text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-foreground">
                          {truncateId(run.id, 8)}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopy(run.id, `run-${run.id}`)}
                          className="hover:text-foreground text-muted-foreground cursor-pointer"
                          title="Copy Run ID"
                        >
                          {copiedId === `run-${run.id}` ? (
                            <Check className="h-3 w-3 text-emerald-400" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </button>
                      </div>
                    </TableCell>

                    <TableCell className="font-mono text-xs text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <Layers className="h-3.5 w-3.5 text-primary shrink-0" />
                        <span>{truncateId(run.scenario_version_id, 6)}</span>
                      </div>
                    </TableCell>

                    <TableCell className="font-mono text-xs text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                        <span>{truncateId(run.policy_id, 6)}</span>
                      </div>
                    </TableCell>

                    <TableCell className="text-xs text-muted-foreground font-mono">
                      {formatDate(run.executed_at)}
                    </TableCell>

                    <TableCell>
                      <span className="rounded bg-emerald-950/60 text-emerald-400 border border-emerald-700/50 px-2 py-0.5 text-[10px] font-bold">
                        SEALED
                      </span>
                    </TableCell>

                    <TableCell className="text-right">
                      <Link href={`/simulations/${run.id}`}>
                        <Button size="sm" variant="outline" className="h-7 text-xs">
                          Inspect
                          <ArrowRight className="h-3 w-3 ml-1" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Academic Explanatory Architecture Card */}
      <div className="rounded-lg border border-border bg-card/60 p-5 space-y-3">
        <h4 className="font-bold text-sm text-foreground flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-primary" />
          The 8-Element Cryptographic Tuple (&Sigma;<sub>run</sub>)
        </h4>
        <p className="text-xs text-muted-foreground leading-relaxed">
          In accordance with Review 2 and IEEE publication requirements, DecisionSphere eliminates black-box ambiguity by locking every execution with:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-2.5 rounded bg-muted/30 border border-border/50">
            <span className="text-muted-foreground block text-[10px] font-sans">1 & 2. Relational Pointers</span>
            <span className="text-foreground font-bold">Scenario & Policy IDs</span>
          </div>
          <div className="p-2.5 rounded bg-muted/30 border border-border/50">
            <span className="text-muted-foreground block text-[10px] font-sans">3. Model Fingerprints</span>
            <span className="text-foreground font-bold">3 &times; SHA-256 Hashes</span>
          </div>
          <div className="p-2.5 rounded bg-muted/30 border border-border/50">
            <span className="text-muted-foreground block text-[10px] font-sans">4 & 5. Source Code & Schema</span>
            <span className="text-foreground font-bold">Git Commit & Migration</span>
          </div>
          <div className="p-2.5 rounded bg-muted/30 border border-border/50">
            <span className="text-muted-foreground block text-[10px] font-sans">6, 7 & 8. Runtime & Clocks</span>
            <span className="text-foreground font-bold">Python, App & UTC Timestamp</span>
          </div>
        </div>
      </div>
    </div>
  );
}
