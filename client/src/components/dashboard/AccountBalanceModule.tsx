import { useCallback, useEffect, useState } from "react";

import { dashboardModulesApi, type AccountBalance } from "../../services/dashboardModulesApi";
import { useAuth } from "../../features/auth/AuthContext";

export const AccountBalanceModule = () => {
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
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading balance…</p>
      </div>
    );
  }

  if (!loading && error && !loaded) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">Account balance</h3>
        <p className="mt-2 text-sm text-slate-600">{error}</p>
        <button
          onClick={loadBalance}
          className="mt-4 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">Account balance</h3>
      {error && <p className="mt-2 text-sm text-slate-600">{error}</p>}
      {balance && (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-md bg-slate-50 p-4">
            <p className="text-xs uppercase text-slate-500">Total paid</p>
            <p className="text-2xl font-semibold text-slate-900">
              {balance.currency} {balance.total_paid.toFixed(2)}
            </p>
          </div>
          <div className="rounded-md bg-slate-50 p-4">
            <p className="text-xs uppercase text-slate-500">Pending</p>
            <p className="text-2xl font-semibold text-slate-900">
              {balance.currency} {balance.total_pending.toFixed(2)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
