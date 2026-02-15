/**
 * DashboardSkeleton — progressive skeleton loaders for the dashboard.
 *
 * Per spec §4.1: use full-page or per-section skeleton loaders that
 * match the dashboard layout. No blank screens or spinners.
 */

interface DashboardSkeletonProps {
  /** Render only a specific section skeleton instead of the full page */
  section?: "developer-hub" | "admin-panel" | "welcome" | "module";
}

function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-md bg-slate-200 ${className}`}
      aria-hidden="true"
    />
  );
}

function ModuleSkeleton() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <SkeletonBlock className="mb-4 h-5 w-1/3" />
      <SkeletonBlock className="mb-3 h-4 w-full" />
      <SkeletonBlock className="mb-3 h-4 w-2/3" />
      <SkeletonBlock className="h-4 w-1/2" />
    </div>
  );
}

function WelcomeSkeleton() {
  return (
    <div className="col-span-full">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <SkeletonBlock className="mb-3 h-7 w-1/3" />
        <SkeletonBlock className="mb-6 h-4 w-1/4" />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-md bg-slate-50 p-4">
              <SkeletonBlock className="mb-2 h-3 w-1/2" />
              <SkeletonBlock className="h-6 w-2/3" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DashboardSkeleton({ section }: DashboardSkeletonProps) {
  if (section === "welcome") return <WelcomeSkeleton />;
  if (section === "module" || section === "developer-hub" || section === "admin-panel") {
    return <ModuleSkeleton />;
  }

  // Full-page skeleton
  return (
    <div
      className="min-h-screen bg-slate-50"
      role="status"
      aria-label="Loading dashboard"
      aria-busy="true"
    >
      {/* Header skeleton */}
      <div className="border-b border-slate-200 bg-white px-6 py-4">
        <SkeletonBlock className="mb-2 h-7 w-40" />
        <SkeletonBlock className="h-4 w-60" />
      </div>

      {/* Content skeleton */}
      <div className="p-4 sm:p-6 lg:p-8">
        <WelcomeSkeleton />
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ModuleSkeleton />
          <ModuleSkeleton />
          <ModuleSkeleton />
          <ModuleSkeleton />
          <ModuleSkeleton />
        </div>
      </div>
    </div>
  );
}
