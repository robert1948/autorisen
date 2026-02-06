import { useEffect, useState } from "react";

import { dashboardModulesApi, type AccountBalance } from "../../services/dashboardModulesApi";

export const AccountBalanceModule = () => {
  const [balance, setBalance] = useState<AccountBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await dashboardModulesApi.getBalance();
        setBalance(data);
      } catch (err) {
        setError((err as Error).message || "Failed to load balance");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Loading balance…</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">Account balance</h3>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
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
