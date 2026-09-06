import * as React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricDisplay } from "@/components/common/MetricDisplay";

describe("MetricDisplay Component", () => {
  it("renders label, value, baseline, and delta shift", () => {
    render(
      <MetricDisplay
        label="Commercial Demand"
        value="6,850 Units"
        baseline="5,840 Units"
        delta="+1,010 Units"
        deltaType="positive"
        epistemicTier="PREDICTED"
        source="XGBoost Regressor"
        meaning="Projected retail demand."
      />
    );

    expect(screen.getByText("Commercial Demand")).toBeInTheDocument();
    expect(screen.getByText("6,850 Units")).toBeInTheDocument();
    expect(screen.getByText("5,840 Units")).toBeInTheDocument();
    expect(screen.getByText(/Δ \+1,010 Units/)).toBeInTheDocument();
    expect(screen.getByText("PREDICTED")).toBeInTheDocument();
    expect(screen.getByText("Projected retail demand.")).toBeInTheDocument();
  });
});
