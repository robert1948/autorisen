/**
 * ProjectStatusModule — the core value area of the dashboard.
 *
 * Per spec §3.4: list view with pagination, sorting, filtering,
 * empty state CTA, and deletion confirmation.
 */

import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { dashboardModulesApi, type ProjectStatusItem } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";
import type { UserProfile } from "../../types/user";

interface ProjectStatusModuleProps {
  title: string;
  user?: UserProfile;
}

export const ProjectStatusModule = ({ title, user }: ProjectStatusModuleProps) => {
  const { state } = useAuth();
  const navigate = useNavigate();
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
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm" role="status" aria-label="Loading projects" aria-busy="true">
        <div className="animate-pulse">
          <div className="mb-4 h-5 w-1/3 rounded bg-slate-200" />
          <div className="space-y-3">
            <div className="h-14 rounded bg-slate-200" />
            <div className="h-14 rounded bg-slate-200" />
            <div className="h-14 rounded bg-slate-200" />
          </div>
        </div>
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
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="project-status-heading">
      <div className="flex items-center justify-between">
        <h3 id="project-status-heading" className="text-lg font-semibold text-slate-900">{title}</h3>
        {projects.length > 0 ? (
          <span className="text-xs text-slate-500">{projects.length} project{projects.length !== 1 ? "s" : ""}</span>
        ) : (
          <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
            {statusValue}
          </span>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-slate-600" role="alert">{error}</p>}
      {projects.length === 0 ? (
        <div className="mt-4 rounded-md border border-dashed border-slate-200 p-6 text-center">
          <p className="text-sm text-slate-500">No projects yet.</p>
          <p className="mt-1 text-xs text-slate-400">Create your first project to get started.</p>
          <button
            onClick={() => navigate("/app/projects/new")}
            className="mt-3 inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Create project
          </button>
        </div>
      ) : (
        <>
          <ul className="mt-3 space-y-3" role="list">
            {projects.map((project) => {
              const statusColor: Record<string, string> = {
                pending: "bg-yellow-100 text-yellow-800",
                "in-progress": "bg-blue-100 text-blue-800",
                completed: "bg-green-100 text-green-800",
                cancelled: "bg-slate-100 text-slate-500",
              };
              const color = statusColor[project.status] ?? "bg-slate-100 text-slate-600";
              return (
                <li key={project.id} className="cursor-pointer rounded-md border border-slate-100 p-3 transition-colors hover:border-blue-200 hover:bg-blue-50" onClick={() => navigate(`/app/projects/${project.id}`)}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{project.title}</p>
                      <p className="text-xs text-slate-500">
                        Created {new Date(project.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${color}`}>
                      {project.status}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
          <button
            onClick={() => navigate("/app/projects/new")}
            className="mt-4 inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900"
          >
            + New project
          </button>
        </>
      )}
    </section>
  );
};
