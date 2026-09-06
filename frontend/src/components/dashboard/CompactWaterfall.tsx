import * as React from "react";
import { FinancialResult } from "@/lib/api/types";
import { formatCurrency } from "@/lib/utils";
import { EpistemicBadge } from "@/components/common/EpistemicBadge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function CompactWaterfall({
  financialResult,
}: {
  financialResult: FinancialResult;
}) {
  const items = [
    {
      name: "Gross Revenue Impact",
      amount: financialResult.gross_revenue_delta,
      type: "revenue",
    },
    {
      name: "Cost of Goods Sold (COGS)",
      amount: financialResult.cogs_delta,
      type: "cost",
    },
    {
      name: "Supply Chain & Expedite Fees",
      amount: financialResult.supply_chain_cost_delta,
      type: "cost",
    },
    {
      name: "Workforce (Overtime & Turnover)",
      amount: financialResult.workforce_cost_delta,
      type: "cost",
    },
    {
      name: "Net Operating Profit Delta",
      amount: financialResult.net_profit_delta,
      type: "profit",
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-base">Managerial Financial Impact</CardTitle>
          <p className="text-xs text-muted-foreground mt-0.5">
            Deterministic accounting aggregation linking demand shifts to variable cost structures.
          </p>
        </div>
        <EpistemicBadge tier="CALCULATED" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map((item) => {
            const isProfit = item.type === "profit";
            const isCost = item.type === "cost";
            const isPositive = item.amount >= 0;

            return (
              <div
                key={item.name}
                className={`flex items-center justify-between p-2.5 rounded-md text-xs border ${
                  isProfit
                    ? "bg-muted/80 font-bold border-border/80"
                    : "bg-muted/30 border-border/40"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      isCost
                        ? "bg-rose-400"
                        : isProfit
                        ? isPositive
                          ? "bg-emerald-400"
                          : "bg-rose-400"
                        : "bg-primary"
                    }`}
                  />
                  <span className="text-foreground">{item.name}</span>
                </div>
                <span
                  className={`font-mono tabular-nums ${
                    isProfit
                      ? isPositive
                        ? "text-emerald-400"
                        : "text-rose-400"
                      : isCost
                      ? "text-rose-300"
                      : "text-foreground"
                  }`}
                >
                  {formatCurrency(item.amount, { showSign: true })}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
