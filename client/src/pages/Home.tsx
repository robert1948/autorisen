import { useEffect, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

type HealthResponse = {
  status: string;
  version?: string;
  env?: string;
};

type HealthState = {
  data?: HealthResponse;
  loading: boolean;
  error?: string;
};

const Home = () => {
  const [state, setState] = useState<HealthState>({ loading: true });

  const fetchHealth = async () => {
    setState({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json: HealthResponse = await res.json();
      setState({ loading: false, data: json });
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setState({ loading: false, error: message });
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const { data, loading, error } = state;

  return (
    <main className="container">
      <section className="card">
        <h1>Autorisen Control Panel</h1>
        <p>Monitor the backend API status and version from the local client.</p>
        <button onClick={fetchHealth} disabled={loading}>
          {loading ? "Checking…" : "Refresh"}
        </button>
      </section>

      <section className="card">
        <h2>Backend Health</h2>
        {loading && <p>Loading health status…</p>}
        {error && (
          <p className="error">Failed to reach API: {error}</p>
        )}
        {!loading && !error && data && (
          <ul>
            <li>
              <strong>Status:</strong> <span className={`badge ${data.status === "ok" ? "badge-ok" : "badge-warn"}`}>{data.status}</span>
            </li>
            {data.version && (
              <li>
                <strong>Version:</strong> {data.version}
              </li>
            )}
            {data.env && (
              <li>
                <strong>Environment:</strong> {data.env}
              </li>
            )}
          </ul>
        )}
      </section>
    </main>
  );
};

export default Home;
