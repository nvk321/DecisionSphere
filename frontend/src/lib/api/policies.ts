import { apiClient } from "./client";
import { AssumptionPolicy, PolicyCreate } from "./types";

export const policiesApi = {
  /**
   * List all assumption policies.
   */
  list: (params?: { skip?: number; limit?: number }) =>
    apiClient<AssumptionPolicy[]>("/api/v1/policies/", {
      method: "GET",
      params,
    }),

  /**
   * Get corporate baseline policy (v1).
   */
  getDefault: () =>
    apiClient<AssumptionPolicy>("/api/v1/policies/default", {
      method: "GET",
    }),

  /**
   * Get policy by ID.
   */
  getById: (policyId: string) =>
    apiClient<AssumptionPolicy>(`/api/v1/policies/${policyId}`, {
      method: "GET",
    }),

  /**
   * Create new immutable policy version.
   */
  create: (payload: PolicyCreate) =>
    apiClient<AssumptionPolicy>("/api/v1/policies/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
