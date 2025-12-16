import fs from "node:fs";
import path from "node:path";

function requireEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

// Extract fileKey + nodeId from a Figma URL
function parseFigmaUrl(url) {
  // Works for links like:
  // https://www.figma.com/file/<FILEKEY>/... ?node-id=123-456
  // https://www.figma.com/design/<FILEKEY>/... ?node-id=123-456
  // https://www.figma.com/board/<FILEKEY>/... ?node-id=123-456
  const m = url.match(/figma\.com\/(file|design|board)\/([^/]+)/);
  if (!m) throw new Error("Could not parse FILEKEY from URL");
  const fileKey = m[2];

  const nodeMatch = url.match(/[?&]node-id=([^&]+)/);
  if (!nodeMatch) throw new Error("URL missing node-id=...");
  const nodeId = decodeURIComponent(nodeMatch[1]); // often like "0-1"

  return { fileKey, nodeId };
}

async function main() {
  const url = process.argv.slice(2).join(" ").trim();
  if (!url) {
    console.error('Usage: node scripts/figma_pull.mjs "<FIGMA_NODE_URL>"');
    process.exit(1);
  }

  // Load env from .env.figma (simple parser to avoid extra deps)
  const envPath = path.resolve(".env.figma");
  if (fs.existsSync(envPath)) {
    const raw = fs.readFileSync(envPath, "utf8");
    for (const line of raw.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eq = trimmed.indexOf("=");
      if (eq === -1) continue;
      const k = trimmed.slice(0, eq).trim();
      const v = trimmed.slice(eq + 1).trim();
      if (!process.env[k]) process.env[k] = v;
    }
  }

  const token = requireEnv("FIGMA_TOKEN");
  const { fileKey, nodeId } = parseFigmaUrl(url);

  const apiUrl = `https://api.figma.com/v1/files/${fileKey}/nodes?ids=${encodeURIComponent(nodeId)}`;

  const resp = await fetch(apiUrl, {
    headers: { "X-FIGMA-TOKEN": token },
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Figma API error ${resp.status}: ${text}`);
  }

  const json = await resp.json();

  const outDir = path.resolve("design/figma");
  fs.mkdirSync(outDir, { recursive: true });

  const safeNode = nodeId.replace(/[^a-zA-Z0-9_-]/g, "_");
  const outFile = path.join(outDir, `${fileKey}__${safeNode}.json`);

  fs.writeFileSync(outFile, JSON.stringify(json, null, 2), "utf8");
  console.log("✅ Saved:", outFile);
  console.log("FileKey:", fileKey);
  console.log("NodeId:", nodeId);
}

main().catch((e) => {
  console.error("❌", e.message);
  process.exit(1);
});
