import { describe, it, expect } from "vitest";
import {
  EPISTEMIC_TIERS,
  DECISION_CATEGORIES,
  RISK_LEVELS,
  VALID_SHIPPING_MODES,
  DEFAULT_POLICY_CONSTANTS,
} from "@/lib/constants";

describe("DecisionSphere Domain Constants", () => {
  it("enforces the exact 6-Tier Epistemic Hierarchy", () => {
    const tiers = Object.keys(EPISTEMIC_TIERS);
    expect(tiers).toHaveLength(6);
    expect(tiers).toContain("OBSERVED");
    expect(tiers).toContain("PREDICTED");
    expect(tiers).toContain("ASSUMED");
    expect(tiers).toContain("PROPAGATED");
    expect(tiers).toContain("CALCULATED");
    expect(tiers).toContain("RECOMMENDED");
  });

  it("defines the 3 authoritative decision categories", () => {
    const categories = Object.keys(DECISION_CATEGORIES);
    expect(categories).toHaveLength(3);
    expect(categories).toContain("PROCEED");
    expect(categories).toContain("PROCEED_WITH_MITIGATIONS");
    expect(categories).toContain("REJECT_RESTRUCTURE");
  });

  it("defines the 4 operational risk levels", () => {
    const levels = Object.keys(RISK_LEVELS);
    expect(levels).toHaveLength(4);
    expect(levels).toContain("LOW");
    expect(levels).toContain("MODERATE");
    expect(levels).toContain("HIGH");
    expect(levels).toContain("SEVERE");
  });

  it("authoritative shipping modes match DataCo pipeline", () => {
    expect(VALID_SHIPPING_MODES).toContain("Standard Class");
    expect(VALID_SHIPPING_MODES).toContain("Second Class");
    expect(VALID_SHIPPING_MODES).toContain("First Class");
    expect(VALID_SHIPPING_MODES).toContain("Same Day");
  });

  it("baseline policy default simplex domain weights sum to 1.0", () => {
    const sum =
      DEFAULT_POLICY_CONSTANTS.crs_w_supply +
      DEFAULT_POLICY_CONSTANTS.crs_w_workforce +
      DEFAULT_POLICY_CONSTANTS.crs_w_demand;
    expect(Math.round(sum * 1000) / 1000).toBe(1.0);
  });
});
