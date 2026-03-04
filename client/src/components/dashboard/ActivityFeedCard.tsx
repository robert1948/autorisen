/**
 * ActivityFeedCard — recent account activity timeline.
 *
 * Fetches real audit events from /api/audit/events and falls back
 * to profile-derived events when audit data is unavailable.
 */

import { useEffect, useState } from "react";
import type { UserProfile } from "../../types/user";
import { apiFetch } from "../../lib/apiFetch";

interface ActivityFeedCardProps {
  user: UserProfile;
}

interface ActivityItem {
  id: string;
  type: "login" | "project" | "system" | "payment" | "agent" | "evidence";
  title: string;
  detail: string;
  timestamp: string;
}

const ACTIVITY_ICONS: Record<ActivityItem["type"], { icon: string; color: string }> = {
  login: { icon: "🔐", color: "bg-blue-100 text-blue-600" },
  project: { icon: "📁", color: "bg-emerald-100 text-emerald-600" },
  system: { icon: "⚙️", color: "bg-slate-100 text-slate-600" },
  payment: { icon: "💳", color: "bg-violet-100 text-violet-600" },
  agent: { icon: "🤖", color: "bg-cyan-100 text-cyan-600" },
  evidence: { icon: "📋", color: "bg-amber-100 text-amber-600" },
};

function timeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(isoDate).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function eventTypeToActivity(eventType: string): ActivityItem["type"] {
  if (eventType.startsWith("login") || eventType === "logout") return "login";
  if (eventType.startsWith("agent") || eventType === "agent_run") return "agent";
  if (eventType.startsWith("evidence") || eventType === "evidence_export") return "evidence";
  if (eventType.startsWith("payment") || eventType.startsWith("payfast")) return "payment";
  if (eventType.startsWith("project")) return "project";
  return "system";
}

function humanizeEventType(eventType: string): string {
  return eventType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function ActivityFeedCard({ user }: ActivityFeedCardProps) {
  const [activities, setActivities] = useState<ActivityItem[]>([]);

  // Fetch real audit events, fall back to profile data
  useEffect(() => {
    let cancelled = false;

    async function fetchAuditEvents() {
      try {
        const data = await apiFetch("/audit/events?limit=8", { auth: true }) as {
          items?: Array<{
            id: string;
            event_type: string;
            created_at: string;
            payload?: Record<string, unknown>;
          }>;
        };
        if (cancelled) return;

        if (data.items && data.items.length > 0) {
          setActivities(
            data.items.map((ev) => ({
              id: ev.id,
              type: eventTypeToActivity(ev.event_type),
              title: humanizeEventType(ev.event_type),
              detail: ev.payload?.detail as string ?? ev.event_type,
              timestamp: ev.created_at,
            }))
          );
          return;
        }
      } catch {
        // Audit endpoint unavailable — fall through to profile-derived data
      }

      if (cancelled) return;

      // Fallback: build from profile
      const items: ActivityItem[] = [];
      if (user.lastLogin) {
        items.push({
          id: "login-latest",
          type: "login",
          title: "Signed in",
          detail: "Session started successfully",
          timestamp: user.lastLogin,
        });
      }
      items.push({
        id: "account-created",
        type: "system",
        title: "Account created",
        detail: `Joined as ${user.role}`,
        timestamp: user.createdAt,
      });
      if (user.emailVerified) {
        items.push({
          id: "email-verified",
          type: "system",
          title: "Email verified",
          detail: user.email,
          timestamp: user.createdAt,
        });
      }
      items.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      setActivities(items.slice(0, 5));
    }

    fetchAuditEvents();
    return () => { cancelled = true; };
  }, [user]);

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
      aria-labelledby="activity-heading"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 id="activity-heading" className="text-base font-semibold text-slate-900 dark:text-white">
          Recent Activity
        </h3>
        <span className="text-xs text-slate-400">{activities.length} events</span>
      </div>

      {activities.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-200 p-6 text-center dark:border-slate-700">
          <p className="text-sm text-slate-500">No activity yet.</p>
        </div>
      ) : (
        <div className="space-y-0">
          {activities.map((item, idx) => {
            const meta = ACTIVITY_ICONS[item.type];
            const isLast = idx === activities.length - 1;
            return (
              <div key={item.id} className="flex gap-3">
                {/* Timeline line + dot */}
                <div className="flex flex-col items-center">
                  <div className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm ${meta.color}`}>
                    {meta.icon}
                  </div>
                  {!isLast && (
                    <div className="w-px flex-1 bg-slate-200 dark:bg-slate-700" />
                  )}
                </div>

                {/* Content */}
                <div className={`flex-1 ${isLast ? "pb-0" : "pb-4"}`}>
                  <div className="flex items-baseline justify-between gap-2">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{item.title}</p>
                    <span className="flex-shrink-0 text-[11px] text-slate-400">{timeAgo(item.timestamp)}</span>
                  </div>
                  <p className="mt-0.5 text-xs text-slate-500">{item.detail}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
