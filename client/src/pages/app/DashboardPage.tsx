/**
 * Dashboard — role-aware, dynamic dashboard page.
 *
 * Implements the Dashboard Content Requirements v2.0:
 *   - §1: Auth-triggered profile fetch via useProfile()
 *   - §2: Role-aware conditional rendering (not CSS hiding)
 *   - §3: All MVP modules with skeleton loading
 *   - §4: Error boundaries, ARIA, responsive grid
 *   - §5: Lazy-loaded developer/admin sections
 *
 * Feature-flagged via VITE_FF_DASHBOARD_V2.
 */

import { Suspense, lazy, useEffect, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ErrorBoundary } from "react-error-boundary";

import { useProfile } from "../../hooks/useProfile";
import { hasPermission } from "../../utils/permissions";
import { DashboardSkeleton } from "../../components/skeletons/DashboardSkeleton";
import { SessionExpired } from "../../components/errors/SessionExpired";
import { DashboardErrorFallback } from "../../components/errors/DashboardErrorFallback";
import { WelcomeHeader } from "../../components/dashboard/WelcomeHeader";
import { AccountDetailsModule } from "../../components/dashboard/AccountDetailsModule";
import { PersonalInfoModule } from "../../components/dashboard/PersonalInfoModule";
import { ProjectStatusModule } from "../../components/dashboard/ProjectStatusModule";
import { AccountBalanceModule } from "../../components/dashboard/AccountBalanceModule";
import { DeleteAccountModule } from "../../components/dashboard/DeleteAccountModule";

// Lazy-load role-specific modules (spec §2.1 — bundle size optimisation)
const DeveloperHubSection = lazy(
  () => import("../../components/dashboard/DeveloperHubSection")
);
const AdminPanel = lazy(
  () => import("../../components/dashboard/AdminPanel")
);

const Dashboard = () => {
  const { user, isLoading, error, refetch } = useProfile();
  const navigate = useNavigate();
  const location = useLocation();

  const isPreview = useMemo(() => {
    const search = new URLSearchParams(location.search);
    return search.get("preview") === "1" || localStorage.getItem("cc_preview_mode") === "true";
  }, [location.search]);

  // If the user is authenticated, exit preview mode permanently
  useEffect(() => {
    if (!isLoading && user && isPreview) {
      localStorage.removeItem("cc_preview_mode");
    }
  }, [isLoading, user, isPreview]);

  // Auth failure redirect (spec §1.4)
  useEffect(() => {
    if (error?.status === 401 || error?.status === 403) {
      if (!isPreview) {
        // Allow SessionExpired component to handle the redirect
      }
    }
  }, [error, isPreview]);

  // Preview mode — read-only placeholder (only when NOT authenticated)
  if (isPreview && !user) {
    return (
      <div className="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
        <div className="mb-6 rounded-md border border-slate-200 bg-white p-4" role="status">
          <p className="text-sm text-slate-700">
            Read-only preview. Sign in to load account data.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
          <div className="h-40 rounded-lg border border-dashed border-slate-200 bg-white" />
        </div>
      </div>
    );
  }

  // Full-page skeleton (spec §4.1 — no blank screens)
  if (isLoading) return <DashboardSkeleton />;

  // Auth errors (spec §1.4)
  if (error?.status === 401 || error?.status === 403) return <SessionExpired />;

  // Non-auth errors with retry
  if (error || !user) {
    return <DashboardErrorFallback error={error} onRetry={refetch} />;
  }

  // Account suspended (spec §1.4)
  if (user.status === "suspended") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
        <div className="mx-auto max-w-md rounded-lg border border-amber-200 bg-white p-8 text-center shadow-sm" role="alert">
          <h2 className="text-lg font-semibold text-amber-800">Account Suspended</h2>
          <p className="mt-2 text-sm text-slate-600">
            Your account has been suspended. Please contact support for assistance.
          </p>
          <a
            href="mailto:support@capecontrol.io"
            className="mt-4 inline-flex items-center rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700"
          >
            Contact Support
          </a>
        </div>
      </div>
    );
  }

  const projectTitle = hasPermission(user, "apikeys:manage")
    ? "Developer projects"
    : "Project status";

  return (
    <ErrorBoundary FallbackComponent={DashboardErrorFallback}>
      <div className="min-h-screen bg-slate-50">
        {/* Offline banner (spec §4.1) */}
        {typeof navigator !== "undefined" && !navigator.onLine && (
          <div className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-center text-sm text-amber-800" role="alert">
            You appear to be offline. Some features may be unavailable.
          </div>
        )}

        <header className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 sm:text-2xl">Dashboard</h1>
            </div>
          </div>
        </header>

        <main
          className="p-4 sm:p-6 lg:p-8"
          role="main"
          aria-label="Dashboard"
        >
          {/* Dashboard grid — responsive per spec §4.5 */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* §3.1 Welcome — always visible, spans full width */}
            <WelcomeHeader user={user} />

            {/* §3.2 Account Details */}
            <AccountDetailsModule user={user} />

            {/* §3.3 Personal Information */}
            <PersonalInfoModule user={user} />

            {/* §3.4 Project Status */}
            <ProjectStatusModule title={projectTitle} user={user} />

            {/* §3.5 Account Balance — visible if user has billing permission */}
            {hasPermission(user, "account:billing") && (
              <AccountBalanceModule user={user} />
            )}

            {/* §3.6 Developer Hub — lazy-loaded, developer + admin only */}
            {hasPermission(user, "apikeys:manage") && (
              <Suspense fallback={<DashboardSkeleton section="developer-hub" />}>
                <DeveloperHubSection user={user} />
              </Suspense>
            )}

            {/* Admin Panel — lazy-loaded, admin only (future) */}
            {hasPermission(user, "admin:users") && (
              <Suspense fallback={<DashboardSkeleton section="admin-panel" />}>
                <AdminPanel user={user} />
              </Suspense>
            )}

            {/* §3.7 Delete Account — always last, danger zone */}
            <div className="col-span-full">
              <DeleteAccountModule user={user} />
            </div>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard;