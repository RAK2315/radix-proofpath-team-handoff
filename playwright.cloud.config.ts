import { defineConfig } from "@playwright/test";

// Intentionally separate from the local suite: no startup, deployment, or personal inputs.
if (!process.env.RADIX_CLOUD_TEST_URL)
  throw new Error(
    "Set RADIX_CLOUD_TEST_URL to the authorized test frontend URL",
  );
export default defineConfig({
  testDir: "./tests/cloud",
  workers: 1,
  timeout: 90000,
  use: {
    baseURL: process.env.RADIX_CLOUD_TEST_URL,
    trace: "retain-on-failure",
  },
});
