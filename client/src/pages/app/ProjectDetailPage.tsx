/**
 * ProjectDetailPage — view, edit, and manage a single project.
 */

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { dashboardModulesApi, type ProjectDetail } from "../../services/dashboardModulesApi";

const STATUS_OPTIONS = ["pending", "in-progress", "completed", "cancelled"] as const;

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  "in-progress": "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-slate-100 text-slate-500",
};

function openCapeAI(placement: string, context?: string) {
  window.dispatchEvent(new CustomEvent("capeai:open", { detail: { placement, prefill: context } }));
}

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [statusVal, setStatusVal] = useState("");
  const [saving, setSaving] = useState(false);

  // Delete state
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // AI instruction sheet state
  const [instructions, setInstructions] = useState<string | null>(null);
  const [instructionsLoading, setInstructionsLoading] = useState(false);
  const [instructionsError, setInstructionsError] = useState<string | null>(null);
  const [planGated, setPlanGated] = useState(false);

  const loadProject = useCallback(async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardModulesApi.getProject(projectId);
      setProject(data);
      setTitle(data.title);
      setDescription(data.description ?? "");
      setStatusVal(data.status);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  const generateInstructions = useCallback(async () => {
    if (!projectId) return;
    setInstructionsLoading(true);
    setInstructionsError(null);
    try {
      const result = await dashboardModulesApi.generateProjectInstructions(projectId);
      setInstructions(result.instructions);
    } catch (err: unknown) {
      const status = (err as { status?: number }).status;
      if (status === 403) {
        setPlanGated(true);
      } else {
        setInstructionsError(err instanceof Error ? err.message : "Failed to generate instructions");
      }
    } finally {
      setInstructionsLoading(false);
    }
  }, [projectId]);

  // Auto-generate instructions once project loads with a description
  useEffect(() => {
    if (project && project.description?.trim() && !instructions && !instructionsLoading && !instructionsError && !planGated) {
      generateInstructions();
    }
  }, [project, instructions, instructionsLoading, instructionsError, planGated, generateInstructions]);


  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    if (!projectId || !title.trim()) return;
    setSaving(true);
    try {
      const updated = await dashboardModulesApi.updateProject(projectId, {
        title: title.trim(),
        description: description.trim() || undefined,
        status: statusVal,
      });
      setProject(updated);
      setEditing(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update project");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!projectId) return;
    setDeleting(true);
    try {
      await dashboardModulesApi.deleteProject(projectId);
      navigate("/app/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete project");
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-1/3 rounded bg-slate-200" />
          <div className="h-4 w-2/3 rounded bg-slate-200" />
          <div className="h-32 rounded bg-slate-200" />
        </div>
      </div>
    );
  }

  if (error && !project) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-red-600">{error}</p>
        <button onClick={() => navigate("/app/dashboard")} className="mt-4 text-sm text-blue-600 hover:underline">
          Back to dashboard
        </button>
      </div>
    );
  }

  if (!project) return null;

  const statusColor = STATUS_COLORS[project.status] ?? "bg-slate-100 text-slate-600";

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button onClick={() => navigate("/app/dashboard")} className="mb-3 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400">
            &larr; Back to dashboard
          </button>
          {editing ? (
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-xl font-bold text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
            />
          ) : (
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{project.title}</h1>
          )}
        </div>
        <span className={`mt-1 rounded-full px-3 py-1 text-xs font-medium ${statusColor}`}>
          {project.status}
        </span>
      </div>

      {error && (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      {/* Details */}
      <div className="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        {editing ? (
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Description</label>
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Status</label>
              <select
                value={statusVal}
                onChange={(e) => setStatusVal(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={saving || !title.trim()}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save changes"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setTitle(project.title);
                  setDescription(project.description ?? "");
                  setStatusVal(project.status);
                  setEditing(false);
                }}
                className="rounded-md px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <>
            <div>
              <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">Description</h3>
              <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
                {project.description || "No description provided."}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 dark:border-slate-700">
              {project.estimated_response_time && (
                <div className="col-span-2 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 dark:border-blue-800 dark:bg-blue-900/20">
                  <h3 className="text-xs font-medium uppercase text-blue-500 dark:text-blue-400">Estimated Response Time</h3>
                  <p className="mt-1 text-sm font-semibold text-blue-700 dark:text-blue-300">
                    {project.estimated_response_time}
                  </p>
                </div>
              )}
              <div>
                <h3 className="text-xs font-medium uppercase text-slate-400">Created</h3>
                <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
                  {new Date(project.created_at).toLocaleString()}
                </p>
              </div>
              {project.updated_at && (
                <div>
                  <h3 className="text-xs font-medium uppercase text-slate-400">Updated</h3>
                  <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
                    {new Date(project.updated_at).toLocaleString()}
                  </p>
                </div>
              )}
              {project.started_at && (
                <div>
                  <h3 className="text-xs font-medium uppercase text-slate-400">Started</h3>
                  <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
                    {new Date(project.started_at).toLocaleString()}
                  </p>
                </div>
              )}
              {project.completed_at && (
                <div>
                  <h3 className="text-xs font-medium uppercase text-slate-400">Completed</h3>
                  <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
                    {new Date(project.completed_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
            <div className="flex gap-3 border-t border-slate-100 pt-4 dark:border-slate-700">
              <button
                onClick={() => setEditing(true)}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
              >
                Edit project
              </button>
            </div>


          </>
        )}
      </div>

      {/* AI-generated instruction sheet */}
      <div className="mt-6 rounded-lg border border-indigo-200 bg-gradient-to-br from-indigo-50 to-blue-50 p-6 shadow-sm dark:border-indigo-800 dark:from-indigo-900/20 dark:to-blue-900/20">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-indigo-900 dark:text-indigo-200">
            Next Steps
          </h2>
          {instructions && (
            <button
              type="button"
              onClick={generateInstructions}
              disabled={instructionsLoading}
              className="text-xs font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-50 dark:text-indigo-400"
            >
              {instructionsLoading ? "Regenerating..." : "Regenerate"}
            </button>
          )}
        </div>

        {instructionsLoading && !instructions && (
          <div className="mt-4 space-y-2">
            <div className="h-4 w-full animate-pulse rounded bg-indigo-200/50" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-indigo-200/50" />
            <div className="h-4 w-4/6 animate-pulse rounded bg-indigo-200/50" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-indigo-200/50" />
            <div className="h-4 w-3/6 animate-pulse rounded bg-indigo-200/50" />
            <p className="mt-2 text-xs text-indigo-500">CapeAI is analysing your project...</p>
          </div>
        )}

        {instructionsError && !instructions && (
          <div className="mt-3">
            <p className="text-sm text-red-600 dark:text-red-400">{instructionsError}</p>
            <button
              type="button"
              onClick={generateInstructions}
              className="mt-2 text-sm font-medium text-indigo-600 hover:underline"
            >
              Try again
            </button>
          </div>
        )}

        {planGated && (
          <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-4 dark:border-amber-700 dark:bg-amber-900/20">
            <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
              AI-generated instruction sheets are available on Pro and Enterprise plans.
            </p>
            <a
              href="/app/pricing"
              className="mt-3 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700"
            >
              Upgrade to Pro
            </a>
          </div>
        )}

        {instructions && (
          <div className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-indigo-900 dark:text-indigo-200">
            {instructions}
          </div>
        )}

        {!instructions && !instructionsLoading && !instructionsError && !planGated && (
          <div className="mt-3">
            <p className="text-sm text-indigo-700 dark:text-indigo-300">
              {project.description?.trim()
                ? "Generate a tailored instruction sheet for this project."
                : "Add a project description, then generate a tailored instruction sheet."}
            </p>
            <button
              type="button"
              onClick={project.description?.trim() ? generateInstructions : () => setEditing(true)}
              className="mt-3 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 active:scale-[0.98]"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {project.description?.trim() ? "Generate instructions" : "Add description first"}
            </button>
          </div>
        )}

        <button
          type="button"
          onClick={() => openCapeAI("project-guidance", `Help me with my project: ${project.title}`)}
          className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-800 dark:text-indigo-400"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          Need more help? Chat with CapeAI
        </button>
      </div>

      {/* Danger zone */}
      <div className="mt-8 rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-900/20">
        <h3 className="text-sm font-semibold text-red-700 dark:text-red-400">Danger zone</h3>
        {confirmDelete ? (
          <div className="mt-3 flex items-center gap-3">
            <p className="text-sm text-red-600 dark:text-red-400">Are you sure? This cannot be undone.</p>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
            >
              {deleting ? "Deleting..." : "Yes, delete"}
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="mt-3 rounded-md border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/40"
          >
            Delete project
          </button>
        )}
      </div>
    </div>
  );
}
