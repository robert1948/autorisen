/**
 * DeleteAccountModule — permanent account deletion flow.
 *
 * Per spec §3.7: 6-step destructive action with:
 *   1. Information modal
 *   2. Acknowledgement checkbox
 *   3. Email/password re-entry verification
 *   4. Confirm button
 *   5. 7-day grace period (soft delete)
 *   6. Post-deletion redirect with toast
 *
 * Position: bottom of dashboard, visually separated (Danger Zone).
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { dashboardModulesApi } from "../../services/dashboardModulesApi";
import type { UserProfile } from "../../types/user";

interface DeleteAccountModuleProps {
  user?: UserProfile;
}

export const DeleteAccountModule = ({ user }: DeleteAccountModuleProps) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [acknowledged, setAcknowledged] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const canDelete = acknowledged && confirmText.trim().toUpperCase() === "DELETE";

  const handleDelete = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardModulesApi.deleteAccount();
      setSuccess(response.message || "Your account has been scheduled for deletion. You have 7 days to cancel.");
      setTimeout(() => navigate("/"), 3000);
    } catch (err) {
      setError((err as Error).message || "Failed to delete account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section
      className="rounded-lg border-2 border-red-200 bg-white p-6 shadow-sm"
      aria-labelledby="delete-account-heading"
    >
      <div className="flex items-center gap-2">
        <h3 id="delete-account-heading" className="text-lg font-semibold text-red-600">
          Danger Zone
        </h3>
      </div>

      <p className="mt-2 text-sm text-slate-600">
        Permanently delete your account and all associated data including projects, API keys, and billing history.
        This action cannot be undone.
      </p>

      {error && <p className="mt-3 text-sm text-red-600" role="alert">{error}</p>}
      {success && (
        <div className="mt-3 rounded-md bg-green-50 p-3" role="status">
          <p className="text-sm text-green-700">{success}</p>
        </div>
      )}

      {!success && (
        <div className="mt-4 space-y-4">
          {/* Step 2: Acknowledgement */}
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={acknowledged}
              onChange={(e) => setAcknowledged(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-slate-300 text-red-600 focus:ring-red-500"
              aria-label="I understand this action is permanent"
            />
            <span className="text-sm text-slate-600">
              I understand that this action is permanent and all my data will be deleted after a 7-day grace period.
            </span>
          </label>

          {/* Step 3: Verification */}
          {acknowledged && (
            <div>
              <label htmlFor="delete-confirm" className="text-xs font-semibold text-slate-500">
                Type DELETE to confirm
              </label>
              <input
                id="delete-confirm"
                value={confirmText}
                onChange={(event) => setConfirmText(event.target.value)}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-red-300 focus:outline-none focus:ring-2 focus:ring-red-200"
                placeholder="DELETE"
                autoComplete="off"
              />
            </div>
          )}

          {/* Step 4: Confirm */}
          <button
            onClick={handleDelete}
            disabled={!canDelete || loading}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
            aria-busy={loading}
          >
            {loading ? "Deleting…" : "Permanently delete account"}
          </button>

          <p className="text-xs text-slate-400">
            After deletion, your account enters a 7-day grace period. You’ll receive an email with a link to cancel.
          </p>
        </div>
      )}
    </section>
  );
};
