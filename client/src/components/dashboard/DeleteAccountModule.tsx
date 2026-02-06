import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { dashboardModulesApi } from "../../services/dashboardModulesApi";

export const DeleteAccountModule = () => {
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const canDelete = confirmText.trim().toUpperCase() === "DELETE";

  const handleDelete = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardModulesApi.deleteAccount();
      setSuccess(response.message);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError((err as Error).message || "Failed to delete account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-red-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-red-600">Delete account</h3>
      <p className="mt-2 text-sm text-slate-600">
        This action will deactivate your account and revoke active sessions.
      </p>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {success && <p className="mt-2 text-sm text-green-600">{success}</p>}
      <div className="mt-4">
        <label className="text-xs font-semibold text-slate-500">Type DELETE to confirm</label>
        <input
          value={confirmText}
          onChange={(event) => setConfirmText(event.target.value)}
          className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
          placeholder="DELETE"
        />
      </div>
      <button
        onClick={handleDelete}
        disabled={!canDelete || loading}
        className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {loading ? "Deleting…" : "Delete account"}
      </button>
    </div>
  );
};
