// ESM wrapper (client/package.json has "type": "module").
// The actual implementation lives in route_guard.cjs.
import { createRequire } from "module";

const require = createRequire(import.meta.url);
require("./route_guard.cjs");
