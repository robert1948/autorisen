import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type ProjectStatusItem } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";

export const ProjectStatusModule = ({ title }: { title: string }) => {
  const { state } = useAuth();
  const [projects, setProjects] = useState<ProjectStatusItem[]>([]);
  const [statusValue, setStatusValue] = useState<string>("Not set");
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await dashboardModulesApi.getProjectStatus();
      setProjects(data.projects ?? []);
      setStatusValue(data.value || "Not set");
      setLoaded(true);
    } catch (err) {
      const message =
        state.status === "authenticated"
          ? "Couldn't load this section. Try again."
          : "Please sign in to view this section.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [state.status]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading project status…</p>
      </div>
    );
  }

  if (!loading && error && !loaded) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{error}</p>
        <button
          onClick={loadProjects}
          className="mt-4 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
          {statusValue}
        </span>
      </div>
      {error && <p className="mt-2 text-sm text-slate-600">{error}</p>}
      {projects.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Status: {statusValue}.</p>
      ) : (
        <ul className="mt-3 space-y-3">
          {projects.map((project) => (
            <li key={project.id} className="rounded-md border border-slate-100 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{project.title}</p>
                  <p className="text-xs text-slate-500">
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
                  {project.status}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
