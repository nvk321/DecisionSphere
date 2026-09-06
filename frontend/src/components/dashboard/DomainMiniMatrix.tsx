import * as React from "react";
import { DomainPrediction } from "@/lib/api/types";
import { MetricDisplay } from "@/components/common/MetricDisplay";
import { formatPercent, formatDelta } from "@/lib/utils";

export interface DomainMiniMatrixProps {
  predictions: DomainPrediction[];
}

export function DomainMiniMatrix({ predictions }: DomainMiniMatrixProps) {
  // Extract domain metrics
  const demandPred = predictions.find((p) => p.domain === "DEMAND");
  const scPred = predictions.find((p) => p.domain === "SUPPLY_CHAIN");
  const wfPred = predictions.find((p) => p.domain === "WORKFORCE");

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Commercial Demand */}
      <MetricDisplay
        label="Commercial Demand Forecast"
        value={
          demandPred
            ? `${Math.round(demandPred.scenario_value).toLocaleString()} Units`
            : "N/A"
        }
        baseline={
          demandPred
            ? `${Math.round(demandPred.baseline_value).toLocaleString()} Units`
            : null
        }
        delta={
          demandPred
            ? `${formatDelta(demandPred.delta_value, "Units", 0)}`
            : null
        }
        deltaType={demandPred && demandPred.delta_value >= 0 ? "positive" : "negative"}
        epistemicTier="PREDICTED"
        source="Phase 2 XGBoost Regressor (WAPE 8.12%)"
        meaning="Projected retail demand volume across 30-day operating horizon."
      />

      {/* Supply Chain Delivery Risk */}
      <MetricDisplay
        label="Logistics Delivery Delay Risk"
        value={
          scPred
            ? formatPercent(scPred.scenario_value, { isRatio: true })
            : "N/A"
        }
        baseline={
          scPred
            ? formatPercent(scPred.baseline_value, { isRatio: true })
            : null
        }
        delta={
          scPred
            ? `${formatDelta((scPred.scenario_value - scPred.baseline_value) * 100, "pp", 1)}`
            : null
        }
        deltaType={
          scPred && scPred.scenario_value > scPred.baseline_value
            ? "negative"
            : "positive"
        }
        epistemicTier="PREDICTED"
        source="Phase 3 Calibrated XGBoost Classifier (ROC-AUC 0.7795)"
        meaning="Calibrated probability of shipment delays exceeding scheduled transit windows."
      />

      {/* Workforce Attrition Risk */}
      <MetricDisplay
        label="Workforce Turnover Risk"
        value={
          wfPred
            ? formatPercent(wfPred.scenario_value, { isRatio: true })
            : "N/A"
        }
        baseline={
          wfPred
            ? formatPercent(wfPred.baseline_value, { isRatio: true })
            : null
        }
        delta={
          wfPred
            ? `${formatDelta((wfPred.scenario_value - wfPred.baseline_value) * 100, "pp", 1)}`
            : null
        }
        deltaType={
          wfPred && wfPred.scenario_value > wfPred.baseline_value
            ? "negative"
            : "positive"
        }
        epistemicTier="PREDICTED"
        source="Phase 4 Calibrated XGBoost Classifier (ROC-AUC 0.8045)"
        meaning="Expected voluntary attrition rate among cohort under applied overtime/wage levels."
      />
    </div>
  );
}
