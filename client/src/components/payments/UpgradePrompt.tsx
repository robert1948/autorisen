/**
 * UpgradePrompt — reusable CTA shown to free-tier users.
 *
 * Variants:
 *  - "sidebar"  → compact card for the sidebar
 *  - "banner"   → full-width banner for dashboard / feature gates
 *  - "inline"   → small inline text link
 */

import { Link } from "react-router-dom";

type Variant = "sidebar" | "banner" | "inline";

interface UpgradePromptProps {
  variant?: Variant;
  /** Optional context message, e.g. "You've used 3/3 agents" */
  message?: string;
  className?: string;
}

export function UpgradePrompt({
  variant = "sidebar",
  message,
  className = "",
}: UpgradePromptProps) {
  if (variant === "inline") {
    return (
      <Link
        to="/app/pricing"
        className={`text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 ${className}`}
      >
        Upgrade to Pro →
      </Link>
    );
  }

  if (variant === "banner") {
    return (
      <div
        className={`rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-4 dark:border-blue-800 dark:from-blue-900/20 dark:to-indigo-900/20 ${className}`}
      >
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200">
              Upgrade to Pro
            </h3>
            <p className="mt-0.5 text-xs text-blue-700 dark:text-blue-400">
              {message || "Unlock 50 agents, 2,500 executions/month, and priority support."}
            </p>
          </div>
          <Link
            to="/app/pricing"
            className="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            View Plans
          </Link>
        </div>
      </div>
    );
  }

  // sidebar (default)
  return (
    <div
      className={`mx-3 mb-3 rounded-lg border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-3 dark:border-blue-800 dark:from-blue-900/20 dark:to-indigo-900/20 ${className}`}
    >
      <div className="flex items-center gap-2">
        <span className="text-lg">⚡</span>
        <span className="text-xs font-semibold text-blue-900 dark:text-blue-200">
          Upgrade to Pro
        </span>
      </div>
      <p className="mt-1 text-[11px] leading-tight text-blue-700 dark:text-blue-400">
        {message || "50 agents, 2,500 runs/mo, priority support"}
      </p>
      <Link
        to="/app/pricing"
        className="mt-2 block rounded-md bg-blue-600 px-3 py-1.5 text-center text-xs font-semibold text-white hover:bg-blue-700"
      >
        View Plans
      </Link>
    </div>
  );
}
