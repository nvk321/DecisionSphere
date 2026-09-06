"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { systemApi } from "@/lib/api/system";
import {
  Menu,
  Activity,
  Fingerprint,
  Moon,
  Sun,
  AlertTriangle,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";

export function Header({
  onMobileMenuToggle,
}: {
  onMobileMenuToggle: () => void;
}) {
  const [isLight, setIsLight] = React.useState(false);

  // Periodic health check
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: systemApi.getHealth,
    refetchInterval: 15000,
  });

  // Periodic model integrity check
  const { data: modelStatus } = useQuery({
    queryKey: ["modelStatus"],
    queryFn: systemApi.getModelStatus,
    refetchInterval: 30000,
  });

  const toggleTheme = () => {
    const root = document.documentElement;
    if (isLight) {
      root.classList.remove("light");
      setIsLight(false);
    } else {
      root.classList.add("light");
      setIsLight(true);
    }
  };

  const isHealthy = health?.status === "healthy" && health.database === "connected";
  const allModelsVerified = modelStatus?.all_verified ?? health?.models_verified ?? true;

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-background/90 px-4 md:px-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMobileMenuToggle}
          className="lg:hidden p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground cursor-pointer"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Global Search Affordance */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md border border-border bg-card/60 text-xs text-muted-foreground w-64 shadow-xs">
          <Search className="h-3.5 w-3.5 opacity-60" />
          <span className="flex-1">Search decisions & levers...</span>
          <kbd className="rounded border border-border/80 bg-muted px-1.5 py-0.5 text-[10px] font-mono">
            ⌘K
          </kbd>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Model Integrity Status Pill */}
        <Link
          href="/system/models"
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer",
            allModelsVerified
              ? "border-emerald-700/40 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/50"
              : "border-rose-600 bg-rose-950/80 text-rose-200 animate-pulse hover:bg-rose-900"
          )}
          title={
            allModelsVerified
              ? "All ML model binaries verified (SHA-256 intact)"
              : "MODEL INTEGRITY FAILURE: Simulation execution disabled"
          }
        >
          {allModelsVerified ? (
            <Fingerprint className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
          )}
          <span className="hidden md:inline">
            {allModelsVerified ? "Models Verified" : "Integrity Failure"}
          </span>
        </Link>

        {/* System Health Pill */}
        <Link
          href="/system/health"
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer",
            isHealthy
              ? "border-border bg-muted/60 text-foreground hover:bg-accent"
              : "border-amber-600/60 bg-amber-950/40 text-amber-300 hover:bg-amber-900/50"
          )}
          title={`Backend status: ${health?.status || "connecting"} | Database: ${
            health?.database || "probing"
          }`}
        >
          <Activity
            className={cn(
              "h-3.5 w-3.5",
              isHealthy ? "text-emerald-400" : "text-amber-400"
            )}
          />
          <span className="hidden sm:inline">
            {isHealthy ? "System Ready" : "Degraded"}
          </span>
        </Link>

        {/* Theme Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={isLight ? "Switch to dark mode" : "Switch to light mode"}
          className="p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
        >
          {isLight ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
        </button>
      </div>
    </header>
  );
}
