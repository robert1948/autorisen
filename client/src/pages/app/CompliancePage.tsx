/**
 * CompliancePage — "Compliance as Comedy" themed compliance dashboard.
 *
 * Per homepage USP §4: "Experience 'Compliance as Comedy': tools and videos
 * that make red tape feel like an engaging spy thriller."
 *
 * Uses existing backend endpoints:
 *   - GET /api/security/stats  — security systems status
 *   - GET /api/health          — system health check
 *   - GET /api/version         — build version
 *
 * Spy-thriller theme: missions, briefings, classified dossiers.
 */

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../lib/apiFetch";

/* ── Types ────────────────────────────────────────── */

interface SecurityStats {
  security_systems: {
    ddos_protection: string;
    input_sanitization: string;
    rate_limiting: string;
  };
  timestamp: string;
}

interface HealthStatus {
  status: string;
  database?: string;
  version?: string;
}

interface ComplianceMission {
  id: string;
  codename: string;
  objective: string;
  status: "classified" | "active" | "complete";
  threat_level: "low" | "medium" | "high";
  detail: string;
}

interface AuditStats {
  total_events: number;
  event_types: Record<string, number>;
  login_attempts: number;
  failed_logins: number;
}

/* ── Main page ────────────────────────────────────── */

export default function CompliancePage() {
  const [security, setSecurity] = useState<SecurityStats | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [auditStats, setAuditStats] = useState<AuditStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [secData, healthData, auditData] = await Promise.all([
        apiFetch<SecurityStats>("/security/stats").catch(() => null),
        apiFetch<HealthStatus>("/health", { auth: false }).catch(() => null),
        apiFetch<AuditStats>("/audit/stats").catch(() => null),
      ]);
      setSecurity(secData);
      setHealth(healthData);
      setAuditStats(auditData);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const res = await fetch("/api/audit/export?format=pdf", {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `evidence-pack-${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert("Failed to export evidence pack. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  // Derive missions from real security data
  const missions = deriveMissions(security, health);
  const completedCount = missions.filter((m) => m.status === "complete").length;
  const clearanceLevel =
    completedCount === missions.length
      ? "TOP SECRET"
      : completedCount >= missions.length - 1
      ? "SECRET"
      : "CONFIDENTIAL";

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-4 sm:p-6">
      {/* Header — Mission Briefing */}
      <header className="relative overflow-hidden rounded-2xl border border-slate-700 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8 shadow-xl dark:border-slate-600">
        <div className="absolute -right-8 -top-8 h-40 w-40 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-blue-500/10 blur-2xl" />

        <div className="relative z-10">
          <div className="mb-1 flex items-center gap-2">
            <span className="inline-flex items-center rounded border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-amber-400">
              {clearanceLevel}
            </span>
            <span className="text-xs text-slate-500">
              {new Date().toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric",
              })}
            </span>
          </div>

          <h1 className="mt-3 text-2xl font-bold text-white sm:text-3xl">
            Mission Briefing: Compliance Status
          </h1>
          <p className="mt-2 max-w-xl text-sm text-slate-400">
            Agent, your organization's security posture is summarized below.
            Each mission represents a critical compliance control.
            Complete all missions to achieve <span className="font-semibold text-emerald-400">TOP SECRET</span> clearance.
          </p>

          <div className="mt-6 flex flex-wrap gap-6">
            <BriefingStat label="Missions" value={`${missions.length}`} />
            <BriefingStat label="Complete" value={`${completedCount}`} accent="green" />
            <BriefingStat label="Clearance" value={clearanceLevel} accent="amber" />
            <BriefingStat
              label="Build"
              value={(health as unknown as Record<string, string>)?.version || "—"}
            />
          </div>
        </div>
      </header>

      {/* Evidence Pack Export */}
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
              <svg className="h-5 w-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Evidence Pack Export
            </h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Generate a compliance-grade PDF with full RAG provenance, document inventory, and audit trail.
            </p>
          </div>
          <button
            onClick={handleExportPDF}
            disabled={exporting}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed dark:focus:ring-offset-slate-900"
          >
            {exporting ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export PDF
              </>
            )}
          </button>
        </div>

        {/* Audit Stats Summary */}
        {auditStats && (
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MiniStat label="Audit Events" value={auditStats.total_events} />
            <MiniStat label="Event Types" value={Object.keys(auditStats.event_types).length} />
            <MiniStat label="Login Attempts" value={auditStats.login_attempts} />
            <MiniStat label="Failed Logins" value={auditStats.failed_logins} accent={auditStats.failed_logins > 0 ? "red" : undefined} />
          </div>
        )}
      </section>

      {/* Loading */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      )}

      {/* Mission Cards */}
      {!loading && (
        <div className="space-y-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-slate-900 dark:text-white">
            <span className="inline-block h-5 w-1.5 rounded-full bg-emerald-500" />
            Active Operations
          </h2>
          {missions.map((mission) => (
            <MissionCard key={mission.id} mission={mission} />
          ))}
        </div>
      )}

      {/* Compliance Tips — "Field Intel" */}
      {!loading && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h2 className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-white">
            <FieldIntelIcon />
            Field Intel: Quick Wins
          </h2>
          <ul className="mt-4 space-y-3">
            <IntelTip
              code="INTEL-001"
              tip="Enable MFA for all admin accounts to achieve maximum clearance."
              status="recommended"
            />
            <IntelTip
              code="INTEL-002"
              tip="Review API keys quarterly — revoke any unused credentials."
              status="recommended"
            />
            <IntelTip
              code="INTEL-003"
              tip="Monitor the Audit Trail for unusual login patterns."
              status="info"
            />
            <IntelTip
              code="INTEL-004"
              tip="Keep your team briefed — share this dashboard with stakeholders."
              status="info"
            />
          </ul>
        </section>
      )}

      {/* Footer */}
      <footer className="pb-6 text-center text-xs text-slate-400 dark:text-slate-500">
        This document is classified under CapeControl compliance policy.
        Unauthorized distribution is subject to review. 🕵️
      </footer>
    </div>
  );
}

/* ── Mission derivation from real data ────────────── */

function deriveMissions(
  security: SecurityStats | null,
  health: HealthStatus | null,
): ComplianceMission[] {
  const missions: ComplianceMission[] = [];

  // Mission 1: DDoS Protection
  const ddosActive = security?.security_systems?.ddos_protection === "active";
  missions.push({
    id: "OP-SHIELD",
    codename: "Operation Shield Wall",
    objective: "DDoS Protection System",
    status: ddosActive ? "complete" : "active",
    threat_level: ddosActive ? "low" : "high",
    detail: ddosActive
      ? "Perimeter defense is active. Token-bucket rate limiter engaged. All inbound traffic is screened."
      : "WARNING: Perimeter defense is offline. Immediate action required.",
  });

  // Mission 2: Input Sanitization
  const sanitizeActive = security?.security_systems?.input_sanitization?.includes("enabled");
  missions.push({
    id: "OP-FILTER",
    codename: "Operation Clean Sweep",
    objective: "Input Sanitization & XSS Prevention",
    status: sanitizeActive ? "complete" : "active",
    threat_level: sanitizeActive ? "low" : "high",
    detail: sanitizeActive
      ? "All user inputs are sanitized. XSS, SQL injection, and prompt injection vectors neutralized."
      : "Input sanitization is not confirmed. Potential injection vectors remain open.",
  });

  // Mission 3: Rate Limiting
  const rlStatus = security?.security_systems?.rate_limiting;
  const rlActive = rlStatus && rlStatus !== "disabled" && rlStatus !== "off";
  missions.push({
    id: "OP-THROTTLE",
    codename: "Operation Slow Hand",
    objective: "API Rate Limiting",
    status: rlActive ? "complete" : "active",
    threat_level: rlActive ? "low" : "medium",
    detail: rlActive
      ? `Rate limiting is engaged (${rlStatus}). Brute-force and abuse vectors are contained.`
      : "Rate limiting is not active. API endpoints may be vulnerable to abuse.",
  });

  // Mission 4: Database Connectivity
  const dbConnected = health?.database === "connected";
  missions.push({
    id: "OP-VAULT",
    codename: "Operation Iron Vault",
    objective: "Database Security & Availability",
    status: dbConnected ? "complete" : "active",
    threat_level: dbConnected ? "low" : "high",
    detail: dbConnected
      ? "Database connection is secure and operational. Data vault integrity confirmed."
      : "Database status unknown or disconnected. Investigate immediately.",
  });

  // Mission 5: System Health
  const systemOk = health?.status === "ok" || health?.status === "healthy";
  missions.push({
    id: "OP-HEARTBEAT",
    codename: "Operation Heartbeat",
    objective: "Core System Health",
    status: systemOk ? "complete" : "active",
    threat_level: systemOk ? "low" : "medium",
    detail: systemOk
      ? "All systems are nominal. Heartbeat confirmed across API and infrastructure layers."
      : "System health check returned an unexpected status. Review /api/health.",
  });

  return missions;
}

/* ── Sub-components ───────────────────────────────── */

function BriefingStat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: "green" | "amber";
}) {
  const valueColor =
    accent === "green"
      ? "text-emerald-400"
      : accent === "amber"
      ? "text-amber-400"
      : "text-white";

  return (
    <div>
      <p className="text-[10px] font-medium uppercase tracking-widest text-slate-500">{label}</p>
      <p className={`text-lg font-bold ${valueColor}`}>{value}</p>
    </div>
  );
}

function MissionCard({ mission }: { mission: ComplianceMission }) {
  const isComplete = mission.status === "complete";

  const borderColor = isComplete
    ? "border-emerald-200 dark:border-emerald-800/50"
    : mission.threat_level === "high"
    ? "border-red-200 dark:border-red-800/50"
    : "border-amber-200 dark:border-amber-800/50";

  const bgAccent = isComplete
    ? "bg-emerald-50 dark:bg-emerald-900/10"
    : mission.threat_level === "high"
    ? "bg-red-50 dark:bg-red-900/10"
    : "bg-amber-50 dark:bg-amber-900/10";

  return (
    <div className={`rounded-xl border ${borderColor} ${bgAccent} p-5 shadow-sm transition-colors`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-center gap-3">
          <MissionStatusIcon complete={isComplete} threat={mission.threat_level} />
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              {mission.id} — {mission.codename}
            </p>
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              {mission.objective}
            </h3>
          </div>
        </div>
        <ThreatBadge level={mission.threat_level} complete={isComplete} />
      </div>
      <p className="mt-3 text-sm leading-relaxed text-slate-600 dark:text-slate-400">
        {mission.detail}
      </p>
    </div>
  );
}

function MissionStatusIcon({
  complete,
  threat,
}: {
  complete: boolean;
  threat: string;
}) {
  if (complete) {
    return (
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/40">
        <svg className="h-5 w-5 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
    );
  }
  const color = threat === "high"
    ? "bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400"
    : "bg-amber-100 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400";
  return (
    <div className={`flex h-9 w-9 items-center justify-center rounded-full ${color}`}>
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    </div>
  );
}

function ThreatBadge({
  level,
  complete,
}: {
  level: string;
  complete: boolean;
}) {
  if (complete) {
    return (
      <span className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-bold uppercase text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
        Secured
      </span>
    );
  }
  const styles =
    level === "high"
      ? "border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400"
      : "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase ${styles}`}>
      Threat: {level}
    </span>
  );
}

function IntelTip({
  code,
  tip,
  status,
}: {
  code: string;
  tip: string;
  status: "recommended" | "info";
}) {
  const accent =
    status === "recommended"
      ? "border-l-amber-500 bg-amber-50/50 dark:bg-amber-900/10"
      : "border-l-blue-500 bg-blue-50/50 dark:bg-blue-900/10";
  return (
    <li className={`rounded-r-md border-l-4 p-3 ${accent}`}>
      <span className="mr-2 font-mono text-xs font-bold text-slate-400">{code}</span>
      <span className="text-sm text-slate-700 dark:text-slate-300">{tip}</span>
    </li>
  );
}

function FieldIntelIcon() {
  return (
    <svg className="h-5 w-5 text-slate-500 dark:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function MiniStat({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: "red";
}) {
  const valColor = accent === "red"
    ? "text-red-600 dark:text-red-400"
    : "text-slate-900 dark:text-white";
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800/50">
      <p className="text-[10px] font-medium uppercase tracking-widest text-slate-500">{label}</p>
      <p className={`text-lg font-bold ${valColor}`}>{value}</p>
    </div>
  );
}
