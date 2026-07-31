import { useEffect, useState } from "react";
import { fetchHealthStatus } from "@/services/healthService";
import type { HealthStatus } from "@/types/health";

/**
 * Root application component.
 *
 * This is a Module 0 bootstrap placeholder that only proves the
 * frontend-backend wiring is correct. Routing, layouts, authentication
 * pages, dashboards, and the AI tutor UI are implemented in Module 12
 * (Frontend), built incrementally against each completed backend
 * module.
 */
function App(): JSX.Element {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealthStatus()
      .then(setHealth)
      .catch(() => setError("Unable to reach the CogniLearn AI backend."));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 text-center">
      <h1 className="text-3xl font-semibold text-slate-900">CogniLearn AI</h1>
      <p className="mt-2 text-slate-600">An Intelligent AI Learning Companion</p>

      <div className="mt-8 rounded-lg border border-slate-200 bg-white px-6 py-4 shadow-sm">
        {error && <p className="text-red-600">{error}</p>}
        {!error && !health && <p className="text-slate-500">Checking backend connection…</p>}
        {health && (
          <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-left text-sm text-slate-700">
            <dt className="font-medium">Status</dt>
            <dd>{health.status}</dd>
            <dt className="font-medium">Service</dt>
            <dd>{health.service}</dd>
            <dt className="font-medium">Version</dt>
            <dd>{health.version}</dd>
            <dt className="font-medium">Environment</dt>
            <dd>{health.environment}</dd>
          </dl>
        )}
      </div>
    </main>
  );
}

export default App;
