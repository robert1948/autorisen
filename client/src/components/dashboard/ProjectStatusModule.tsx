import { useEffect, useState } from "react";

import { dashboardModulesApi, type ProjectStatusItem } from "../../services/dashboardModulesApi";

export const ProjectStatusModule = ({ title }: { title: string }) => {
  const [projects, setProjects] = useState<ProjectStatusItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await dashboardModulesApi.getProjects();
        setProjects(data);
      } catch (err) {
        setError((err as Error).message || "Failed to load project status");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading project status…</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {projects.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No projects yet.</p>
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
