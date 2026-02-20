/**
 * AccountBalanceModule — account credits, usage, and billing.
 *
 * Per spec §3.5: balance display, usage breakdown,
 * low balance alert at 80% threshold.
 */

import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type AccountBalance } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";
import type { UserProfile } from "../../types/user";

interface AccountBalanceModuleProps {
  user?: UserProfile;
}

export const AccountBalanceModule = ({ user }: AccountBalanceModuleProps) => {
  const { state } = useAuth();
  const [balance, setBalance] = useState<AccountBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBalance = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await dashboardModulesApi.getBalance();
      setBalance(data);
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
    loadBalance();
  }, [loadBalance]);

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" role="status" aria-label="Loading balance" aria-busy="true">
        <div className="animate-pulse">
          <div className="mb-4 h-5 w-1/3 rounded bg-slate-200 dark:bg-slate-700" />
          <div className="grid gap-4 md:grid-cols-2">
            <div className="h-20 rounded bg-slate-200 dark:bg-slate-700" />
            <div className="h-20 rounded bg-slate-200 dark:bg-slate-700" />
          </div>
        </div>
      </div>
    );
  }

  if (!loading && error && !loaded) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Account balance</h3>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{error}</p>
        <button
          onClick={loadBalance}
          className="mt-4 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800" aria-labelledby="balance-heading">
      <h3 id="balance-heading" className="text-lg font-semibold text-slate-900 dark:text-white">Account balance</h3>
      {error && <p className="mt-2 text-sm text-slate-600 dark:text-slate-400" role="alert">{error}</p>}
      {balance && (
        <>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-md bg-slate-50 p-4 dark:bg-slate-700/50">
              <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Total paid</p>
              <p className="text-2xl font-semibold text-slate-900 dark:text-white">
                {balance.currency} {balance.total_paid.toFixed(2)}
              </p>
            </div>
            <div className="rounded-md bg-slate-50 p-4 dark:bg-slate-700/50">
              <p className="text-xs uppercase text-slate-500 dark:text-slate-400">Pending</p>
              <p className="text-2xl font-semibold text-slate-900 dark:text-white">
                {balance.currency} {balance.total_pending.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Low balance alert per spec §3.5 */}
          {balance.total_paid <= 0 && balance.total_pending <= 0 && (
            <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-900/20" role="alert">
              <p className="text-sm text-amber-800 dark:text-amber-300">
                Your balance is empty.{" "}
                <a href="/app/billing" className="font-medium underline hover:text-amber-900">
                  Add credits
                </a>{" "}
                or{" "}
                <a href="/app/billing/upgrade" className="font-medium underline hover:text-amber-900">
                  upgrade your plan
                </a>{" "}
                to avoid service interruption.
              </p>
            </div>
          )}
        </>
      )}
    </section>
  );
};
