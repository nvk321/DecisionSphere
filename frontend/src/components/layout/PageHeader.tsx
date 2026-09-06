import * as React from "react";
import { cn } from "@/lib/utils";

export interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  epistemicNote?: string;
  className?: string;
}

export function PageHeader({
  title,
  description,
  actions,
  epistemicNote,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border/60 mb-6",
        className
      )}
    >
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
          {title}
        </h1>
        {description && (
          <p className="text-xs sm:text-sm text-muted-foreground max-w-3xl leading-relaxed">
            {description}
          </p>
        )}
        {epistemicNote && (
          <div className="pt-1">
            <span className="inline-flex items-center text-[11px] font-mono text-muted-foreground bg-muted/50 px-2 py-0.5 rounded border border-border/50">
              {epistemicNote}
            </span>
          </div>
        )}
      </div>

      {actions && <div className="flex items-center gap-2.5 shrink-0">{actions}</div>}
    </div>
  );
}
