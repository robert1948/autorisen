/**
 * DashboardErrorFallback — error boundary fallback for the dashboard.
 *
 * Per spec §4.1:
 *   - API error (non-auth): inline error with "Retry" button
 *   - Network offline: banner at top
 *   - Profile service unavailable (503): retry with exponential backoff (max 3)
 */

interface DashboardErrorFallbackProps {
  error?: unknown;
  onRetry?: () => void;
  resetErrorBoundary?: () => void;
}

export function DashboardErrorFallback({
  error,
  onRetry,
  resetErrorBoundary,
}: DashboardErrorFallbackProps) {
  const errorObj = error as { status?: number; message?: string } | Error | null | undefined;
  const status = errorObj && "status" in errorObj ? (errorObj as { status?: number }).status : undefined;
  const message = errorObj && "message" in errorObj ? (errorObj as { message?: string }).message : "Something went wrong loading the dashboard.";

  const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
  const isServiceDown = status === 503;

  const handleRetry = () => {
    if (resetErrorBoundary) resetErrorBoundary();
    if (onRetry) onRetry();
  };

  return (
    <div
      className="flex min-h-[60vh] items-center justify-center bg-slate-50 p-4"
      role="alert"
      aria-live="polite"
    >
      <div className="mx-auto max-w-lg rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        {isOffline ? (
          <>
            <h2 className="text-lg font-semibold text-slate-900">You appear to be offline</h2>
            <p className="mt-2 text-sm text-slate-600">
              Some features may be unavailable. Please check your connection and try again.
            </p>
          </>
        ) : isServiceDown ? (
          <>
            <h2 className="text-lg font-semibold text-slate-900">Service temporarily unavailable</h2>
            <p className="mt-2 text-sm text-slate-600">
              We're having trouble loading your profile. Please try again in a moment.
            </p>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-slate-900">Something went wrong</h2>
            <p className="mt-2 text-sm text-slate-600">{message}</p>
          </>
        )}

        <button
          onClick={handleRetry}
          className="mt-6 inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
