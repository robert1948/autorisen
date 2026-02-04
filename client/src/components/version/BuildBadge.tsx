import React, { useEffect, useState } from "react";

type BuildInfo = {
  buildVersion: string;
  gitSha?: string;
};

let cachedBuildInfo: BuildInfo | null = null;
let buildInfoPromise: Promise<BuildInfo | null> | null = null;

const fetchBuildInfo = () => {
  if (cachedBuildInfo) {
    return Promise.resolve(cachedBuildInfo);
  }

  if (!buildInfoPromise) {
    buildInfoPromise = fetch("/api/version", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) return null;
        const data = await response.json().catch(() => null);
        if (!data || typeof data !== "object") return null;

        const rawBuildVersion =
          typeof (data as { buildVersion?: unknown }).buildVersion === "string"
            ? (data as { buildVersion: string }).buildVersion
            : typeof (data as { version?: unknown }).version === "string"
              ? (data as { version: string }).version
              : null;

        if (!rawBuildVersion) return null;

        const gitSha =
          typeof (data as { gitSha?: unknown }).gitSha === "string"
            ? (data as { gitSha: string }).gitSha
            : typeof (data as { git_sha?: unknown }).git_sha === "string"
              ? (data as { git_sha: string }).git_sha
              : undefined;

        const result = { buildVersion: String(rawBuildVersion), gitSha };
        cachedBuildInfo = result;
        return result;
      })
      .catch(() => null);
  }

  return buildInfoPromise;
};

const BuildBadge: React.FC = () => {
  const [buildInfo, setBuildInfo] = useState<BuildInfo | null>(cachedBuildInfo);

  useEffect(() => {
    let mounted = true;
    fetchBuildInfo().then((info) => {
      if (mounted) setBuildInfo(info);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (!buildInfo?.buildVersion) return null;

  const shortSha = buildInfo.gitSha ? buildInfo.gitSha.slice(0, 7) : null;
  const label = shortSha
    ? `Build ${buildInfo.buildVersion} • ${shortSha}`
    : `Build ${buildInfo.buildVersion}`;

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
