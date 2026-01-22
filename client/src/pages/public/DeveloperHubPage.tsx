import React from "react";
import { Link } from "react-router-dom";

export default function DeveloperHubPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto w-full max-w-3xl px-4 py-14 sm:px-8">
        <h1 className="text-3xl font-semibold tracking-tight">Developer Hub</h1>
        <p className="mt-3 text-sm text-slate-300">
          This page is currently being prepared.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            to="/api-docs"
            className="inline-flex items-center rounded-full border border-slate-800/80 bg-slate-900/40 px-4 py-2 text-sm text-slate-200 hover:border-slate-700 hover:text-white transition"
          >
            API docs placeholder
          </Link>
          <Link
            to="/docs"
            className="inline-flex items-center rounded-full border border-slate-800/80 bg-slate-900/40 px-4 py-2 text-sm text-slate-200 hover:border-slate-700 hover:text-white transition"
          >
            View docs
          </Link>
        </div>
      </div>
    </div>
  );
}
