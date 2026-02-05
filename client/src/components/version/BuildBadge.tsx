import React, { useEffect, useState } from "react";

type BuildInfo = {
  version?: string;
  gitSha?: string;
  buildEpoch?: string;
};

let cachedBuildInfo: BuildInfo | null = null;
let buildInfoPromise: Promise<BuildInfo | null> | null = null;
const STORAGE_KEY = "capecontrol-build-info";

const normalizeValue = (value?: string | null) => {
  if (!value) return null;
  const cleaned = value.trim();
  if (!cleaned || cleaned.toLowerCase() === "unknown") return null;
  return cleaned;
};

const readStoredBuildInfo = (): BuildInfo | null => {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as BuildInfo;
    if (!parsed || typeof parsed !== "object") return null;
    return parsed;
  } catch (err) {
    console.warn("Failed to read build info cache", err);
    return null;
  }
};

const storeBuildInfo = (info: BuildInfo | null) => {
  if (typeof window === "undefined" || !info) return;
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(info));
  } catch (err) {
    console.warn("Failed to cache build info", err);
  }
};

const fetchBuildInfo = () => {
  if (!cachedBuildInfo) {
    cachedBuildInfo = readStoredBuildInfo();
  }
  if (cachedBuildInfo) return Promise.resolve(cachedBuildInfo);

  if (!buildInfoPromise) {
    buildInfoPromise = fetch("/api/version", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) return null;
        const data = await response.json().catch(() => null);
        if (!data || typeof data !== "object") return null;

        const raw = data as {
          buildVersion?: unknown;
          version?: unknown;
          app_version?: unknown;
          gitSha?: unknown;
          git_sha?: unknown;
          buildEpoch?: unknown;
          build_epoch?: unknown;
        };

        const version =
          normalizeValue(typeof raw.app_version === "string" ? raw.app_version : null) ??
          normalizeValue(typeof raw.version === "string" ? raw.version : null) ??
          normalizeValue(typeof raw.buildVersion === "string" ? raw.buildVersion : null);
        const gitSha =
          normalizeValue(typeof raw.gitSha === "string" ? raw.gitSha : null) ??
          normalizeValue(typeof raw.git_sha === "string" ? raw.git_sha : null);
        const buildEpoch =
          normalizeValue(typeof raw.buildEpoch === "string" ? raw.buildEpoch : null) ??
          normalizeValue(typeof raw.build_epoch === "string" ? raw.build_epoch : null);

        if (!version && !gitSha) return null;

        const result: BuildInfo = {
          version: version ?? undefined,
          gitSha: gitSha ?? undefined,
          buildEpoch: buildEpoch ?? undefined,
        };
        cachedBuildInfo = result;
        storeBuildInfo(result);
        return result;
      })
      .catch(() => null);
  }

  return buildInfoPromise;
};

const BuildBadge: React.FC = () => {
  const [buildInfo, setBuildInfo] = useState<BuildInfo | null>(
    cachedBuildInfo ?? readStoredBuildInfo(),
  );

  useEffect(() => {
    let mounted = true;
    fetchBuildInfo().then((info) => {
      if (mounted) setBuildInfo(info);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const version = normalizeValue(buildInfo?.version ?? null);
  const gitSha = normalizeValue(buildInfo?.gitSha ?? null);
  const buildEpoch = normalizeValue(buildInfo?.buildEpoch ?? null);
  if (!version && !gitSha && !buildEpoch) return null;

  const shortSha = gitSha ? gitSha.slice(0, 7) : null;
  const label = version && shortSha
    ? `v${version} · ${shortSha}`
    : version
      ? `v${version}`
      : shortSha
        ? `build ${shortSha}`
        : `build ${buildEpoch}`;

  return (
    <span
      className="text-xs font-mono text-slate-500/70"
      aria-label={label}
    >
      {label}
    </span>
  );
};

export default BuildBadge;
