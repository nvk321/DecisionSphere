import * as React from "react";
import { cn } from "@/lib/utils";
import { EPISTEMIC_TIERS, EpistemicTier } from "@/lib/constants";
import { Sparkles, Sliders, Calculator, Compass, Link2, Database } from "lucide-react";

export interface EpistemicBadgeProps {
  tier: EpistemicTier | string;
  showIcon?: boolean;
  className?: string;
}

export function EpistemicBadge({
  tier,
  showIcon = true,
  className,
}: EpistemicBadgeProps) {
  const normalizedTier = (tier?.toUpperCase() || "CALCULATED") as EpistemicTier;
  const meta = EPISTEMIC_TIERS[normalizedTier] || EPISTEMIC_TIERS.CALCULATED;

  const getIcon = () => {
    switch (normalizedTier) {
      case "OBSERVED":
        return <Database className="h-3 w-3 mr-1" aria-hidden="true" />;
      case "PREDICTED":
        return <Sparkles className="h-3 w-3 mr-1 text-violet-400" aria-hidden="true" />;
      case "ASSUMED":
        return <Sliders className="h-3 w-3 mr-1 text-sky-400" aria-hidden="true" />;
      case "PROPAGATED":
        return <Link2 className="h-3 w-3 mr-1 text-amber-400" aria-hidden="true" />;
      case "CALCULATED":
        return <Calculator className="h-3 w-3 mr-1 text-emerald-400" aria-hidden="true" />;
      case "RECOMMENDED":
        return <Compass className="h-3 w-3 mr-1 text-purple-400" aria-hidden="true" />;
      default:
        return null;
    }
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase transition-colors select-none",
        meta.badgeClass,
        className
      )}
      title={`${meta.label}: ${meta.description}`}
      aria-label={`Epistemic tier: ${meta.label} - ${meta.description}`}
    >
      {showIcon && getIcon()}
      <span>{meta.label}</span>
    </span>
  );
}
