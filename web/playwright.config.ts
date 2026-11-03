import { defineConfig, devices } from "@playwright/test";

// The stack (web, API, workers, Postgres, Redis, MinIO) must already be running. CI brings it up with
// compose.e2e.yml; locally point E2E_BASE_URL at the web server and E2E_API_URL at the API.
export default defineConfig({
  testDir: "./e2e",
  globalSetup: "./e2e/global-setup.ts",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
