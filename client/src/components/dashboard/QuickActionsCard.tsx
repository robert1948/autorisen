/**
 * QuickActionsCard — primary call-to-action buttons for the dashboard.
 *
 * Shows contextual quick actions based on user role:
 *   - Create project (all)
 *   - View marketplace (all)
 *   - Manage agents (developer/admin)
 *   - Open chat (developer/admin)
 */

import { useNavigate } from "react-router-dom";
import { hasPermission } from "../../utils/permissions";
import { features } from "../../config/features";
import type { UserProfile } from "../../types/user";

interface QuickActionsCardProps {
  user: UserProfile;
}

interface ActionItem {
  label: string;
  description: string;
  to: string;
  icon: React.ReactNode;
  accent: string;
}

export function QuickActionsCard({ user }: QuickActionsCardProps) {
  const navigate = useNavigate();

  const actions: ActionItem[] = [
    {
      label: "New Project",
      description: "Start a new project",
      to: "/app/projects/new",
      accent: "from-blue-500 to-blue-600",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
    },
    {
      label: "Marketplace",
      description: "Browse agents & flows",
      to: "/app/marketplace",
      accent: "from-emerald-500 to-emerald-600",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
        </svg>
      ),
    },
  ];

  if (features.agentsShell && hasPermission(user, "apikeys:manage")) {
    actions.push({
      label: "Agents",
      description: "Manage your agents",
      to: "/app/agents",
      accent: "from-violet-500 to-violet-600",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
    });
  }

  if (features.agentsShell) {
    actions.push({
      label: "Chat",
      description: "Open console",
      to: "/app/chat",
      accent: "from-amber-500 to-orange-500",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
    });
  }

  return (
    <section aria-labelledby="quick-actions-heading">
      <h3 id="quick-actions-heading" className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
        Quick Actions
      </h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {actions.map((action) => (
          <button
            key={action.to}
            onClick={() => navigate(action.to)}
            className="group flex flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:border-slate-300 hover:shadow-md active:scale-[0.98] dark:border-slate-700 dark:bg-slate-800"
          >
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${action.accent} text-white shadow-sm`}>
              {action.icon}
            </div>
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{action.label}</span>
            <span className="hidden text-[10px] text-slate-400 sm:block">{action.description}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
