import { apiClient } from "./client";
import {
  CRSWeightSweepItem,
  CRSWeightSweepRequest,
  DemandShockSweepItem,
  DemandShockSweepRequest,
  FinancialSweepItem,
  FinancialSweepRequest,
  FlipThresholdResponse,
  FlipThresholdSearchRequest,
} from "./types";

export const sensitivityApi = {
  /**
   * Experiment B: Retail demand shock sweep across response curves.
   */
  demandSweep: (payload: DemandShockSweepRequest) =>
    apiClient<DemandShockSweepItem[]>("/api/v1/sensitivity/demand-sweep", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  /**
   * Experiment D: Financial coupling parameter 1D sweep.
   */
  financialSweep: (payload: FinancialSweepRequest) =>
    apiClient<FinancialSweepItem[]>("/api/v1/sensitivity/financial-sweep", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  /**
   * Multi-criteria CRS domain weight simplex sweep.
   */
  crsSweep: (payload: CRSWeightSweepRequest) =>
    apiClient<CRSWeightSweepItem[]>("/api/v1/sensitivity/crs-weight-sweep", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  /**
   * Decision boundary flip threshold search.
   */
  tippingPoint: (payload: FlipThresholdSearchRequest) =>
    apiClient<FlipThresholdResponse>("/api/v1/sensitivity/tipping-point", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
