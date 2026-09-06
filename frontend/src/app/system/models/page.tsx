"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { systemApi } from "@/lib/api/system";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { copyToClipboard } from "@/lib/utils";
import { Fingerprint, CheckCircle2, AlertTriangle, ShieldCheck, Copy, Check, RefreshCw } from "lucide-react";

export default function ModelIntegrityPage() {
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null);

  const { data: statusResponse, isLoading, error, refetch } = useQuery({
    queryKey: ["modelStatus"],
    queryFn: () => systemApi.getModelStatus(),
  });

  const handleCopy = async (text: string, key: string) => {
    const ok = await copyToClipboard(text);
    if (ok) {
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    }
  };

  const allVerified = statusResponse?.all_verified ?? false;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Learning Model Integrity (Gate I)"
        description="Cryptographic SHA-256 fingerprint verification of frozen predictive model binaries. Prevents execution against corrupt or unverified artifacts."
        epistemicNote="Gate I ensures that all PREDICTED inferences originate from authoritative serialized models."
        actions={
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Re-verify Fingerprints
          </Button>
        }
      />

      {error && (
        <ErrorBanner
          title="Failed to Probe Model Integrity"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {/* Global Status Banner */}
      {!isLoading && statusResponse && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between ${
            allVerified
              ? "border-emerald-700/60 bg-emerald-950/30 text-emerald-200"
              : "border-rose-700/60 bg-rose-950/30 text-rose-200"
          }`}
        >
          <div className="flex items-center gap-3">
            {allVerified ? (
              <ShieldCheck className="h-8 w-8 text-emerald-400 shrink-0" />
            ) : (
              <AlertTriangle className="h-8 w-8 text-rose-400 shrink-0" />
            )}
            <div>
              <h3 className="text-base font-bold">
                {allVerified
                  ? "All 3 ML Model Binaries Cryptographically Verified"
                  : "MODEL INTEGRITY FAILURE: Unsafe Artifacts Detected"}
              </h3>
              <p className="text-xs opacity-90 mt-0.5">
                {allVerified
                  ? "SHA-256 checksums match the frozen baselines established in Review 1 and Review 2."
                  : "Simulation execution has been disabled. DecisionSphere refuses to simulate against unverified binaries."}
              </p>
            </div>
          </div>
          <span className="font-mono text-xs uppercase px-2 py-1 rounded bg-black/40 font-bold">
            {statusResponse.status}
          </span>
        </div>
      )}

      {isLoading && <TableSkeleton rows={4} />}

      {!isLoading && statusResponse?.models && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Fingerprint className="h-4 w-4 text-primary" />
              Serialized Artifact Descriptors & Signatures
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Model Domain & Algorithm</TableHead>
                  <TableHead>Expected SHA-256 Hash</TableHead>
                  <TableHead>Observed On-Disk Hash</TableHead>
                  <TableHead>Filesystem Status</TableHead>
                  <TableHead className="text-right">Verification</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(statusResponse.models).map(([key, model]) => {
                  const isMatch = model.verified;

                  return (
                    <TableRow key={key}>
                      <TableCell>
                        <div className="space-y-0.5">
                          <span className="font-bold text-xs text-foreground block">
                            {model.name}
                          </span>
                          <span className="font-mono text-[11px] text-muted-foreground block">
                            {model.path}
                          </span>
                        </div>
                      </TableCell>

                      <TableCell className="font-mono text-xs text-muted-foreground">
                        <div className="flex items-center gap-1.5">
                          <span>{model.expected_sha256.slice(0, 16)}...</span>
                          <button
                            type="button"
                            onClick={() => handleCopy(model.expected_sha256, `${key}-exp`)}
                            className="hover:text-foreground text-muted-foreground cursor-pointer"
                            title="Copy Expected Hash"
                          >
                            {copiedKey === `${key}-exp` ? (
                              <Check className="h-3 w-3 text-emerald-400" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </button>
                        </div>
                      </TableCell>

                      <TableCell className="font-mono text-xs">
                        <div className="flex items-center gap-1.5">
                          <span className={isMatch ? "text-foreground" : "text-rose-400 font-bold"}>
                            {model.actual_sha256 ? `${model.actual_sha256.slice(0, 16)}...` : "NONE"}
                          </span>
                          {model.actual_sha256 && (
                            <button
                              type="button"
                              onClick={() => handleCopy(model.actual_sha256!, `${key}-act`)}
                              className="hover:text-foreground text-muted-foreground cursor-pointer"
                              title="Copy Actual Hash"
                            >
                              {copiedKey === `${key}-act` ? (
                                <Check className="h-3 w-3 text-emerald-400" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </button>
                          )}
                        </div>
                      </TableCell>

                      <TableCell>
                        <span className="text-xs font-mono">
                          {model.exists ? (
                            <span className="text-emerald-400">FOUND</span>
                          ) : (
                            <span className="text-rose-400 font-bold">MISSING</span>
                          )}
                        </span>
                      </TableCell>

                      <TableCell className="text-right">
                        <span
                          className={`font-mono text-xs font-bold px-2 py-0.5 rounded border ${
                            isMatch
                              ? "border-emerald-600 bg-emerald-950/40 text-emerald-300"
                              : "border-rose-600 bg-rose-950/40 text-rose-300"
                          }`}
                        >
                          {model.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
