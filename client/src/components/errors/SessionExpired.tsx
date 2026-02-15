/**
 * SessionExpired — displayed when the user's token is invalid or expired.
 *
 * Per spec §1.4:
 *   401 → attempt silent refresh; if failed, show this with toast
 *   403 → redirect to login immediately
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function SessionExpired() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/auth/login", { replace: true });
    }, 3000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div
      className="flex min-h-screen items-center justify-center bg-slate-50"
      role="alert"
      aria-live="assertive"
    >
      <div className="mx-auto max-w-md rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
          <svg className="h-6 w-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-lg font-semibold text-slate-900">Session expired</h2>
        <p className="mt-2 text-sm text-slate-600">
          Your session has expired. Please sign in again.
        </p>
        <button
          onClick={() => navigate("/auth/login", { replace: true })}
          className="mt-6 inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Sign in
        </button>
      </div>
    </div>
  );
}
