/*
 * Build guard: archive is quarantined reference-only code.
 * - Nothing in src/ (outside src/archive/) may import from src/archive/.
 */

const fs = require("fs");
const path = require("path");

const PROJECT_ROOT = path.join(__dirname, "..");
const SRC_ROOT = path.join(PROJECT_ROOT, "src");
const ARCHIVE_ROOT = path.join(SRC_ROOT, "archive");

/** @param {string} dir */
function listSourceFiles(dir) {
  /** @type {string[]} */
  const out = [];

  /** @param {string} current */
  function walk(current) {
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (full === ARCHIVE_ROOT) continue;
        if (entry.name === "node_modules") continue;
        if (entry.name.startsWith(".")) continue;
        walk(full);
        continue;
      }

      if (!/\.(ts|tsx|js|jsx)$/.test(entry.name)) continue;
      out.push(full);
    }
  }

  walk(dir);
  return out;
}

/** @param {string} filePath */
function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function main() {
  if (!fs.existsSync(ARCHIVE_ROOT)) {
    console.log("archive_guard: OK (no src/archive)");
    return;
  }

  const files = listSourceFiles(SRC_ROOT);

  /** @type {Array<{file: string, line: number, text: string}>} */
  const hits = [];

  // Catch static + dynamic imports, re-exports, and require()
  const patterns = [
    /\bfrom\s+["'][^"']*\/archive\b[^"']*["']/,
    /\bimport\s*\(\s*["'][^"']*\/archive\b[^"']*["']\s*\)/,
    /\brequire\s*\(\s*["'][^"']*\/archive\b[^"']*["']\s*\)/,
  ];

  for (const file of files) {
    const text = readText(file);
    const lines = text.split(/\r?\n/);

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!line.includes("archive")) continue;

      for (const re of patterns) {
        if (re.test(line)) {
          hits.push({
            file: path.relative(PROJECT_ROOT, file),
            line: i + 1,
            text: line.trim(),
          });
          break;
        }
      }
    }
  }

  if (hits.length) {
    console.error("archive_guard: FAILED (imports from src/archive are forbidden)");
    for (const hit of hits) {
      console.error(`- ${hit.file}:${hit.line} ${hit.text}`);
    }
    process.exit(1);
  }

  console.log("archive_guard: OK (no imports from src/archive)");
}

main();
