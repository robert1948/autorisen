/**
 * CreateProjectPage — simple form to create a new project.
 */

import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { dashboardModulesApi } from "../../services/dashboardModulesApi";

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      await dashboardModulesApi.createProject({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      navigate("/app/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create project. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Create a new project</h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        Projects help you organise and track your work on the platform.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
            {error}
          </div>
        )}

        <div>
          <label htmlFor="project-title" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Project title <span className="text-red-500">*</span>
          </label>
          <input
            id="project-title"
            type="text"
            required
            maxLength={200}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Q1 Marketing Analysis"
            className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
          />
        </div>

        <div>
          <label htmlFor="project-description" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Description
          </label>
          <textarea
            id="project-description"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Briefly describe what this project is about..."
            className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={submitting || !title.trim()}
            className="inline-flex items-center rounded-md bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Create project"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/app/dashboard")}
            className="rounded-md px-4 py-2.5 text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
