/**
 * AdminPanel — admin-only dashboard section.
 *
 * Per spec §2.2: Admin visibility includes:
 *   - Global metrics and analytics
 *   - User management (view, suspend, modify roles)
 *   - Feature flag management
 *   - System health dashboard
 *
 * Status: Stub — Admin role is planned for future implementation.
 * MFA enforcement and reduced session timeout (10 min) required.
 */

import type { UserProfile } from "../../types/user";

interface AdminPanelProps {
  user: UserProfile;
}

export default function AdminPanel({ user }: AdminPanelProps) {
  return (
    <div className="col-span-full">
      <div className="rounded-lg border border-purple-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100">
            <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Admin Panel</h2>
            <p className="text-sm text-slate-500">System administration and user management</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <AdminStatCard label="Total Users" value="—" />
          <AdminStatCard label="Active Sessions" value="—" />
          <AdminStatCard label="System Health" value="Operational" accent="green" />
          <AdminStatCard label="Feature Flags" value="—" />
        </div>

        <div className="mt-6 rounded-md border border-dashed border-purple-200 p-4 text-center">
          <p className="text-sm text-purple-600">
            Full admin panel coming soon. MFA enforcement and audit logging required.
          </p>
        </div>
      </div>
    </div>
  );
}

function AdminStatCard({
  label,
  value,
  accent = "slate",
}: {
  label: string;
  value: string;
  accent?: "green" | "slate";
}) {
  return (
    <div className="rounded-md bg-purple-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-purple-500">{label}</p>
      <p className={`mt-1 text-lg font-semibold ${accent === "green" ? "text-green-700" : "text-slate-900"}`}>
        {value}
      </p>
    </div>
  );
}
