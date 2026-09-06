import * as React from "react";
import { cn } from "@/lib/utils";
import { EpistemicBadge } from "./EpistemicBadge";
import { EpistemicTier } from "@/lib/constants";
import { Info } from "lucide-react";

export interface MetricDisplayProps {
  label: string;
  value: string | React.ReactNode;
  baseline?: string | null;
  delta?: string | null;
  deltaType?: "neutral" | "positive" | "negative" | "warning";
  epistemicTier?: EpistemicTier | string;
  source?: string;
  meaning?: string;
  actionGuidance?: string;
  className?: string;
}

export function MetricDisplay({
  label,
  value,
  baseline,
  delta,
  deltaType = "neutral",
  epistemicTier,
  source,
  meaning,
  actionGuidance,
  className,
}: MetricDisplayProps) {
  const deltaColorMap = {
    neutral: "text-muted-foreground",
    positive: "text-emerald-400 font-semibold",
    negative: "text-rose-400 font-semibold",
    warning: "text-amber-400 font-semibold",
  };

  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-4 flex flex-col justify-between space-y-2",
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </span>
        {epistemicTier && (
          <EpistemicBadge tier={epistemicTier} showIcon={false} />
        )}
      </div>

      <div className="my-1">
        <div className="text-2xl font-bold tracking-tight text-foreground tabular-nums">
          {value}
        </div>
        {(baseline || delta) && (
          <div className="flex items-center gap-2 mt-1 text-xs tabular-nums flex-wrap">
            {baseline && (
              <span className="text-muted-foreground">
                Base: <span className="font-medium text-foreground/80">{baseline}</span>
              </span>
            )}
            {delta && (
              <span className={cn("inline-flex items-center", deltaColorMap[deltaType])}>
                &Delta; {delta}
              </span>
            )}
          </div>
        )}
      </div>

      {(source || meaning || actionGuidance) && (
        <div className="pt-2 border-t border-border/40 text-[11px] text-muted-foreground leading-relaxed flex items-start gap-1.5">
          <Info className="h-3 w-3 shrink-0 mt-0.5 opacity-70" />
          <div className="space-y-0.5">
            {meaning && <p>{meaning}</p>}
            {source && (
              <p className="opacity-80">
                <span className="font-semibold">Source:</span> {source}
              </p>
            )}
            {actionGuidance && (
              <p className="text-foreground/90 font-medium">
                <span className="font-semibold">Action:</span> {actionGuidance}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
