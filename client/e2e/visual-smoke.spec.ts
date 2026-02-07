import { expect, test } from "@playwright/test";
import fs from "fs";
import path from "path";

const dateStamp = new Date().toISOString().split("T")[0];
const evidenceDir = path.resolve(process.cwd(), "..", "docs", "evidence", "ui", dateStamp);

async function registerAndSeedAuth(page: import("@playwright/test").Page) {
  const email = `ui-smoke-${Date.now()}@example.com`;
  const password = "Password123!@#";
  const csrfResp = await page.request.get("/api/auth/csrf");
  const csrfBody = await csrfResp.json();
  const csrfToken = csrfBody.token ?? csrfBody.csrf_token;

  const registerResp = await page.request.post("/api/auth/register", {
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    data: {
      first_name: "UI",
      last_name: "Smoke",
      email,
      password,
      confirm_password: password,
      terms_accepted: true,
      role: "Customer",
      company_name: "CapeControl",
      recaptcha_token: "dummy",
    },
  });

  const registerJson = await registerResp.json();
  let accessToken: string | undefined = registerJson.access_token;
  if (!accessToken) {
    const loginResp = await page.request.post("/api/auth/login", {
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
      data: {
        email,
        password,
      },
    });
    const loginJson = await loginResp.json();
    accessToken = loginJson.access_token;
  }

  if (!accessToken) {
    throw new Error("Unable to obtain access token for UI smoke test");
  }

  await page.addInitScript((token: string) => {
    localStorage.setItem(
      "autorisen-auth",
      JSON.stringify({ accessToken: token }),
    );
  }, accessToken);

  await page.addInitScript(() => {
    localStorage.setItem("onboarding_explore_quietly", "true");
    localStorage.setItem("cc_preview_mode", "true");
  });
}

function ensureEvidenceDir() {
  fs.mkdirSync(evidenceDir, { recursive: true });
}

test.describe("UI visual smoke", () => {
  test("onboarding welcome", async ({ page }) => {
    ensureEvidenceDir();
    await registerAndSeedAuth(page);
    await page.goto("/onboarding/welcome", { waitUntil: "networkidle" });

    await expect(
      page.getByText("Enable CapeAI guided onboarding tips"),
    ).toBeVisible();
    await expect(
      page.getByText("CapeAI will explain each step as you go."),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Start setup" })).toBeVisible();

    await page.screenshot({
      path: path.join(evidenceDir, "onboarding-welcome.png"),
      fullPage: true,
    });
  });

  test("dashboard preview", async ({ page }) => {
    ensureEvidenceDir();
    await registerAndSeedAuth(page);
    await page.goto("/app/dashboard?preview=1", { waitUntil: "networkidle" });

    const authErrors = page.locator("text=/Not authenticated|Unauthorized|session expired/i");
    await expect(authErrors).toHaveCount(0);

    await page.screenshot({
      path: path.join(evidenceDir, "dashboard-preview.png"),
      fullPage: true,
    });
  });
});
