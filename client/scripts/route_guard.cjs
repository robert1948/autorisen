/*
Route regression guard: ensure the root route "/" stays wired to the branded Landing.

This is a deterministic build-time check intended to prevent silent routing regressions
(e.g. accidentally swapping "/" to MVP scaffold pages).
*/

const fs = require("fs");
const path = require("path");

const appTsxPath = path.join(__dirname, "..", "src", "App.tsx");

function fail(message) {
  // eslint-disable-next-line no-console
  console.error(`route_guard: ${message}`);
  process.exit(1);
}

let appSource;
try {
  appSource = fs.readFileSync(appTsxPath, "utf8");
} catch (error) {
  fail(`Unable to read ${appTsxPath}: ${error && error.message ? error.message : String(error)}`);
}

// Hard invariants:
// - Must have a root route entry.
// - Must *not* wire root to MvpLanding.
// - Must wire root to the canonical branded landing component (LandingMinimal).
const hasRootRoute = /<Route\s+path=\"\/\"/m.test(appSource);
if (!hasRootRoute) {
  fail('Missing root route "/" in App.tsx');
}

const rootToMvpLanding = /<Route\s+path=\"\/\"\s+element=\{<MvpLanding\s*\/>\}\s*\/>/m.test(appSource);
if (rootToMvpLanding) {
  fail('Root route "/" is wired to <MvpLanding /> (scaffold). Must remain branded landing.');
}

const rootToLandingMinimal = /<Route\s+path=\"\/\"\s+element=\{<LandingMinimal\s*\/>\}\s*\/>/m.test(appSource);
if (!rootToLandingMinimal) {
  fail('Root route "/" is not wired to <LandingMinimal /> (canonical).');
}

// eslint-disable-next-line no-console
console.log('route_guard: OK ("/" -> branded landing)');
