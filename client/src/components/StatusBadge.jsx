import { useEffect, useState } from "react";

export default function StatusBadge() {
  const [front, setFront] = useState(null);
  const [back, setBack] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    fetch("/version.json")
      .then(r => r.json())
      .then(setFront)
      .catch(() => setFront(null));

    fetch("/api/status")
      .then(r => r.json())
      .then(setBack)
      .catch(() => setErr("Backend status unavailable"));
  }, []);

  const pill = (txt) => (
    <span className="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium bg-gray-100">
      {txt}
    </span>
  );

  return (
    <div className="fixed bottom-3 right-3 z-50 flex flex-col gap-1 text-[11px] text-gray-700">
      {front && pill(`FE ${front.version} · ${front.git_sha.slice(0,7)}`)}
      {back && pill(`BE ${back.version} · ${back.git_sha.slice(0,7)} · ${back.environment}`)}
      {err && <span className="text-red-600">{err}</span>}
    </div>
  );
}
