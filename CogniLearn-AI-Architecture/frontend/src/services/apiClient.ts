import axios from "axios";

/**
 * Base API client for CogniLearn AI.
 *
 * All frontend services communicate with the backend exclusively
 * through this client. Endpoint-specific service modules (auth,
 * courses, assessments, learner, adaptive, ai, analytics) will be
 * added under `src/services/` as each backend module is implemented.
 *
 * Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 7 - Frontend Package Structure)
 */

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
