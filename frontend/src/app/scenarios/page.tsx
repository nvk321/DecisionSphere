"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { scenariosApi } from "@/lib/api/scenarios";
import { ScenarioCreate } from "@/lib/api/types";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorBanner } from "@/components/common/ErrorBanner";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDate } from "@/lib/utils";
import { Plus, Sliders, Play, Archive, CheckCircle2, ArrowRight } from "lucide-react";

export default function ScenariosPage() {
  const queryClient = useQueryClient();
  const [createModalOpen, setCreateModalOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [formError, setFormError] = React.useState<string | null>(null);

  // Fetch scenarios list
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["scenarios"],
    queryFn: () => scenariosApi.list({ limit: 50, include_archived: false }),
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (payload: ScenarioCreate) => scenariosApi.create(payload),
    onSuccess: (newScenario) => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      setCreateModalOpen(false);
      setName("");
      setDescription("");
      setFormError(null);
      // Route to the new scenario workspace
      window.location.href = `/scenarios/${newScenario.id}`;
    },
    onError: (err: any) => {
      setFormError(err.message || "Failed to create scenario.");
    },
  });

  // Archive mutation
  const archiveMutation = useMutation({
    mutationFn: (scenarioId: string) => scenariosApi.archive(scenarioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setFormError("Scenario name is required.");
      return;
    }
    createMutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      initial_levers: {
        demand_growth_pct: 0.0,
        promo_active: false,
        scheduled_days_offset: 0,
        shipping_mode_override: null,
        overtime_workforce_pct: 0.0,
        salary_hike_override: null,
      },
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scenario Workspace"
        description="Define, parameterize, and manage business scenarios with immutable parameter versions."
        epistemicNote="Scenarios hold user-defined ASSUMED levers evaluated by authoritative models."
        actions={
          <Button onClick={() => setCreateModalOpen(true)}>
            <Plus className="h-4 w-4 mr-1.5" />
            Create Scenario
          </Button>
        }
      />

      {error && (
        <ErrorBanner
          title="Failed to Load Scenarios"
          message={(error as Error).message}
          onRetry={() => refetch()}
        />
      )}

      {isLoading && <TableSkeleton rows={6} />}

      {!isLoading && data?.items && data.items.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Active Business Scenarios</CardTitle>
            <p className="text-xs text-muted-foreground">
              Select a scenario to configure what-if levers, compare versions, or execute simulations.
            </p>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Scenario Title</TableHead>
                  <TableHead>Latest Version</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((scenario) => {
                  const latestVer =
                    scenario.versions && scenario.versions.length > 0
                      ? scenario.versions[scenario.versions.length - 1]
                      : null;

                  return (
                    <TableRow key={scenario.id}>
                      <TableCell>
                        <Link
                          href={`/scenarios/${scenario.id}`}
                          className="font-semibold text-foreground hover:underline flex items-center gap-2"
                        >
                          <Sliders className="h-4 w-4 text-primary shrink-0" />
                          <span>{scenario.name}</span>
                        </Link>
                        {scenario.description && (
                          <p className="text-xs text-muted-foreground truncate max-w-md mt-0.5">
                            {scenario.description}
                          </p>
                        )}
                      </TableCell>

                      <TableCell className="font-mono text-xs">
                        <span className="rounded bg-muted px-2 py-0.5 font-bold">
                          v{latestVer?.version_number ?? 1}
                        </span>
                      </TableCell>

                      <TableCell className="text-xs text-muted-foreground font-mono">
                        {formatDate(scenario.created_at)}
                      </TableCell>

                      <TableCell>
                        <span className="inline-flex items-center text-xs text-emerald-400 font-semibold gap-1">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Active
                        </span>
                      </TableCell>

                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Link href={`/scenarios/${scenario.id}`}>
                            <Button size="sm" variant="outline" className="h-8 text-xs">
                              Workspace
                              <ArrowRight className="h-3 w-3 ml-1" />
                            </Button>
                          </Link>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-8 text-xs text-rose-400 hover:bg-rose-950/30"
                            onClick={() => {
                              if (confirm(`Archive scenario "${scenario.name}"?`)) {
                                archiveMutation.mutate(scenario.id);
                              }
                            }}
                          >
                            <Archive className="h-3.5 w-3.5" />
                          </Button>
                        </div>
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
          icon={<Sliders className="h-8 w-8 text-primary" />}
          title="No Scenarios Configured"
          description="Create your first strategic scenario to parameterize operational levers and run multi-domain simulations."
          actionLabel="Create Scenario"
          onAction={() => setCreateModalOpen(true)}
        />
      )}

      {/* Creation Modal */}
      <Dialog open={createModalOpen} onOpenChange={setCreateModalOpen}>
        <DialogContent onClose={() => setCreateModalOpen(false)}>
          <DialogHeader>
            <DialogTitle>Create Strategic Scenario</DialogTitle>
            <DialogDescription>
              A scenario defines a hypothetical business decision context. Initial baseline levers (v1) will be initialized automatically.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateSubmit} className="space-y-4">
            {formError && (
              <div className="rounded-md border border-rose-800 bg-rose-950/60 p-3 text-xs text-rose-200">
                {formError}
              </div>
            )}

            <div className="space-y-1.5">
              <label htmlFor="scenario-name" className="text-xs font-semibold text-foreground">
                Scenario Title *
              </label>
              <Input
                id="scenario-name"
                placeholder="e.g. Q4 Holiday Promo & Expedited Fulfillment"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={200}
                required
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="scenario-desc" className="text-xs font-semibold text-foreground">
                Description / Strategic Intent
              </label>
              <textarea
                id="scenario-desc"
                rows={3}
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                placeholder="Provide rationale or organizational objectives for this scenario..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={2000}
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Initialize Scenario"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
