"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Sliders,
  PlayCircle,
  History,
  FlaskConical,
  ShieldCheck,
  FileText,
  Fingerprint,
  Activity,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: "OVERVIEW",
    items: [{ name: "Dashboard", href: "/", icon: LayoutDashboard }],
  },
  {
    title: "DECISIONS",
    items: [
      { name: "Scenarios", href: "/scenarios", icon: Sliders },
      { name: "Simulate", href: "/simulate", icon: PlayCircle },
    ],
  },
  {
    title: "ANALYSIS",
    items: [
      { name: "Simulation Runs", href: "/simulations", icon: History },
      { name: "Sensitivity Lab", href: "/sensitivity", icon: FlaskConical },
    ],
  },
  {
    title: "GOVERNANCE",
    items: [
      { name: "Policies", href: "/policies", icon: ShieldCheck },
      { name: "Audit & Provenance", href: "/audit", icon: FileText },
    ],
  },
  {
    title: "SYSTEM",
    items: [
      { name: "Model Integrity", href: "/system/models", icon: Fingerprint },
      { name: "System Health", href: "/system/health", icon: Activity },
    ],
  },
];

export function Sidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r border-border bg-card/95 backdrop-blur transition-all duration-200 flex flex-col justify-between",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div>
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          <Link
            href="/"
            className="flex items-center gap-2.5 overflow-hidden transition-opacity hover:opacity-90"
          >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground font-extrabold text-base shadow-sm">
              DS
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-sm tracking-tight text-foreground">
                  DecisionSphere
                </span>
                <span className="text-[10px] text-muted-foreground font-mono tracking-wider">
                  INTELLIGENCE
                </span>
              </div>
            )}
          </Link>

          <button
            type="button"
            onClick={onToggle}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="hidden lg:flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-foreground transition-colors cursor-pointer"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        </div>

        {/* Nav Links */}
        <nav className="space-y-6 px-3 py-4 overflow-y-auto max-h-[calc(100vh-8rem)]">
          {NAV_GROUPS.map((group) => (
            <div key={group.title} className="space-y-1">
              {!collapsed && (
                <h4 className="px-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/80 mb-2">
                  {group.title}
                </h4>
              )}
              <ul className="space-y-1">
                {group.items.map((item) => {
                  const isActive =
                    item.href === "/"
                      ? pathname === "/"
                      : pathname.startsWith(item.href);
                  const Icon = item.icon;

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-md px-3 py-2 text-xs font-medium transition-colors cursor-pointer",
                          isActive
                            ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                            : "text-muted-foreground hover:bg-accent hover:text-foreground",
                          collapsed && "justify-center px-2"
                        )}
                        title={collapsed ? item.name : undefined}
                      >
                        <Icon className="h-4 w-4 shrink-0" />
                        {!collapsed && <span>{item.name}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </div>

      {/* Footer Info */}
      {!collapsed && (
        <div className="p-4 border-t border-border/60 text-[11px] text-muted-foreground flex flex-col gap-1">
          <div className="flex items-center justify-between font-mono">
            <span>TRL 4 Prototype</span>
            <span className="text-emerald-400 font-semibold">● ACTIVE</span>
          </div>
          <span className="text-[10px] opacity-70">SCOPE, VIT • 2026</span>
        </div>
      )}
    </aside>
  );
}
