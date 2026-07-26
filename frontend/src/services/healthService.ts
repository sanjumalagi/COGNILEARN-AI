import apiClient from "./apiClient";
import type { HealthStatus } from "@/types/health";

/**
 * Fetches backend liveness/version information.
 *
 * Used only to verify the frontend-backend integration during the
 * Module 0 bootstrap; domain-specific services follow in later modules.
 */
export async function fetchHealthStatus(): Promise<HealthStatus> {
  const response = await apiClient.get<HealthStatus>("/health");
  return response.data;
}
