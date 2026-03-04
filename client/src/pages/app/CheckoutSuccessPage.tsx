/**
 * CheckoutSuccessPage — PayFast payment return page.
 *
 * After a successful PayFast checkout, the user is redirected here.
 * The page polls the backend to verify the payment actually completed
 * (ITN may arrive slightly after the redirect) and shows real data.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { apiFetch } from "../../lib/apiFetch";

type InvoiceStatus = "pending" | "paid" | "failed" | "cancelled" | "refunded";

interface LatestInvoice {
  id: string;
  invoice_number: string | null;
  amount: string;
  currency: string;
  status: InvoiceStatus;
  item_name: string;
  created_at: string;
}

const STATUS_CONFIG: Record<InvoiceStatus, { icon: string; label: string; color: string; bg: string }> = {
  paid: { icon: "✓", label: "Payment Successful", color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800" },
  pending: { icon: "⏳", label: "Processing Payment", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800" },
  failed: { icon: "✕", label: "Payment Failed", color: "text-red-600 dark:text-red-400", bg: "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800" },
  cancelled: { icon: "–", label: "Payment Cancelled", color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800" },
  refunded: { icon: "↩", label: "Payment Refunded", color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800" },
};

const MAX_POLLS = 12; // 12 x 3s = 36 seconds max
const POLL_INTERVAL = 3000;

export default function CheckoutSuccess() {
  const [searchParams] = useSearchParams();
  const [invoice, setInvoice] = useState<LatestInvoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollCount = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const pfPaymentId = searchParams.get("pf_payment_id");

  const fetchStatus = useCallback(async (): Promise<boolean> => {
    try {
      const data = await apiFetch<LatestInvoice>("/payments/status/latest", { auth: true });
      setInvoice(data);
      setIsLoading(false);

      // Keep polling if still pending and under limit
      if (data.status === "pending" && pollCount.current < MAX_POLLS) {
        pollCount.current += 1;
        return false; // not done
      }
      return true; // done
    } catch {
      setError("Unable to verify payment status. Your payment may still be processing.");
      setIsLoading(false);
      return true; // stop polling on error
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const done = await fetchStatus();
      if (!cancelled && !done) {
        timerRef.current = setTimeout(poll, POLL_INTERVAL);
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [fetchStatus]);

  const status = invoice?.status ?? "pending";
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4 dark:bg-slate-950">
      <div className="w-full max-w-md">
        <div className={`rounded-xl border p-8 text-center shadow-sm ${config.bg}`}>
          {/* Status icon */}
          <div className={`mx-auto flex h-16 w-16 items-center justify-center rounded-full ${status === "paid" ? "bg-emerald-100 dark:bg-emerald-900/40" : status === "pending" ? "bg-blue-100 dark:bg-blue-900/40" : "bg-red-100 dark:bg-red-900/40"}`}>
            {isLoading ? (
              <svg className="h-8 w-8 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <span className={`text-3xl font-bold ${config.color}`}>{config.icon}</span>
            )}
          </div>

          {/* Title */}
          <h1 className={`mt-4 text-xl font-bold ${config.color}`}>
            {isLoading ? "Verifying Payment…" : config.label}
          </h1>

          {/* Description */}
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            {isLoading
              ? "We're confirming your payment with PayFast. This usually takes a few seconds."
              : status === "paid"
                ? "Thank you! Your payment has been confirmed and your account has been updated."
                : status === "pending"
                  ? "Your payment is still being processed by PayFast. It should complete shortly — check your billing page for updates."
                  : "Something went wrong with your payment. Please check your billing page or try again."}
          </p>

          {/* Payment details */}
          {invoice && !isLoading && (
            <div className="mt-6 rounded-lg bg-white/60 p-4 text-left dark:bg-slate-800/40">
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500 dark:text-slate-400">Item</dt>
                  <dd className="font-medium text-slate-900 dark:text-white">{invoice.item_name}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500 dark:text-slate-400">Amount</dt>
                  <dd className="font-medium text-slate-900 dark:text-white">
                    {invoice.currency} {parseFloat(invoice.amount).toFixed(2)}
                  </dd>
                </div>
                {invoice.invoice_number && (
                  <div className="flex justify-between">
                    <dt className="text-slate-500 dark:text-slate-400">Invoice</dt>
                    <dd className="font-mono text-xs text-slate-700 dark:text-slate-300">{invoice.invoice_number}</dd>
                  </div>
                )}
                {pfPaymentId && (
                  <div className="flex justify-between">
                    <dt className="text-slate-500 dark:text-slate-400">PayFast Ref</dt>
                    <dd className="font-mono text-xs text-slate-700 dark:text-slate-300">{pfPaymentId}</dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          {error && (
            <p className="mt-4 text-sm text-amber-600 dark:text-amber-400">{error}</p>
          )}

          {/* Actions */}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link
              to="/app/dashboard"
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Go to Dashboard
            </Link>
            <Link
              to="/app/billing"
              className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-center text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              View Billing
            </Link>
          </div>
        </div>

        {/* Pending polling indicator */}
        {!isLoading && status === "pending" && (
          <p className="mt-4 text-center text-xs text-slate-400">
            Still waiting for PayFast confirmation. You can safely close this page — your billing page will update automatically.
          </p>
        )}
      </div>
    </div>
  );
}
