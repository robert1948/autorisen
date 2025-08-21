// scripts/write-version.cjs
const fs = require("fs");
const path = require("path");

const APP_VERSION = process.env.VITE_APP_VERSION || "dev";
const GIT_SHA     = process.env.VITE_GIT_SHA || "local";
const BUILD_TIME  = process.env.VITE_BUILD_TIME || new Date().toISOString();

const payload = { app: "capecontrol-frontend", version: APP_VERSION, git_sha: GIT_SHA, build_time: BUILD_TIME };

const publicOut = path.join(__dirname, "..", "client", "public", "version.json");
fs.writeFileSync(publicOut, JSON.stringify(payload, null, 2));
console.log("Wrote", publicOut, payload);
