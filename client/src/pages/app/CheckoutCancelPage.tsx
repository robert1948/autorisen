/**
 * CheckoutCancelPage — PayFast payment cancellation page.
 *
 * Shown when the user cancels during PayFast checkout.
 * Provides context about what happened and clear next-step actions.
 */

import { Link } from "react-router-dom";

export default function CheckoutCancel() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4 dark:bg-slate-950">
      <div className="w-full max-w-md">
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-8 text-center shadow-sm dark:border-amber-800 dark:bg-amber-900/20">
          {/* Icon */}
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/40">
            <span className="text-3xl">✕</span>
          </div>

          {/* Title */}
          <h1 className="mt-4 text-xl font-bold text-amber-700 dark:text-amber-400">
            Payment Cancelled
          </h1>

          {/* Description */}
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Your payment was cancelled and you have not been charged. If this was
            a mistake, you can try again from the pricing page.
          </p>

          {/* Reasons / FAQ */}
          <div className="mt-6 rounded-lg bg-white/60 p-4 text-left dark:bg-slate-800/40">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Common reasons for cancellation</h2>
            <ul className="mt-2 list-inside list-disc space-y-1 text-xs text-slate-500 dark:text-slate-400">
              <li>Changed your mind about the plan</li>
              <li>Need to check payment details first</li>
              <li>Want to review features before upgrading</li>
              <li>Session timed out on PayFast</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link
              to="/app/pricing"
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-center text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              View Plans
            </Link>
            <Link
              to="/app/dashboard"
              className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-center text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              Go to Dashboard
            </Link>
          </div>
        </div>

        <p className="mt-4 text-center text-xs text-slate-400">
          Need help? Contact us at{" "}
          <a href="mailto:support@cape-control.com" className="underline hover:text-slate-600 dark:hover:text-slate-300">
            support@cape-control.com
          </a>
        </p>
      </div>
    </div>
  );
}
