import { apiClient } from "./client";
import {
  PaginatedResponse,
  Scenario,
  ScenarioCreate,
  ScenarioUpdate,
  ScenarioVersion,
  SimulationDetail,
  SimulationRequest,
} from "./types";

export const scenariosApi = {
  /**
   * List strategic scenarios.
   */
  list: (params?: { skip?: number; limit?: number; include_archived?: boolean }) =>
    apiClient<PaginatedResponse<Scenario>>("/api/v1/scenarios/", {
      method: "GET",
      params,
    }),

  /**
   * Create a new scenario.
   */
  create: (payload: ScenarioCreate) =>
    apiClient<Scenario>("/api/v1/scenarios/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  /**
   * Get scenario by ID.
   */
  getById: (scenarioId: string) =>
    apiClient<Scenario>(`/api/v1/scenarios/${scenarioId}`, {
      method: "GET",
    }),

  /**
   * Update scenario metadata or levers (Gate G: levers increment version).
   */
  update: (scenarioId: string, payload: ScenarioUpdate) =>
    apiClient<Scenario>(`/api/v1/scenarios/${scenarioId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  /**
   * Soft-archive scenario.
   */
  archive: (scenarioId: string) =>
    apiClient<Scenario>(`/api/v1/scenarios/${scenarioId}`, {
      method: "DELETE",
    }),

  /**
   * List immutable versions for a scenario.
   */
  listVersions: (scenarioId: string) =>
    apiClient<ScenarioVersion[]>(`/api/v1/scenarios/${scenarioId}/versions`, {
      method: "GET",
    }),

  /**
   * Get specific version.
   */
  getVersion: (scenarioId: string, versionId: string) =>
    apiClient<ScenarioVersion>(`/api/v1/scenarios/${scenarioId}/versions/${versionId}`, {
      method: "GET",
    }),

  /**
   * Run simulation directly for scenario.
   */
  run: (scenarioId: string, payload?: SimulationRequest) =>
    apiClient<SimulationDetail>(`/api/v1/scenarios/${scenarioId}/run`, {
      method: "POST",
      body: payload ? JSON.stringify(payload) : undefined,
    }),
};
