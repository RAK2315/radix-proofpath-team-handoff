import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  timeout: 60000,
  retries: 0,
  use: {
    baseURL: "http://127.0.0.1:5179",
    viewport: { width: 1440, height: 1100 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `"${resolve(process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python")}" -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8123`,
      url: "http://127.0.0.1:8123/api/health",
      reuseExistingServer: false,
      env: {
        RADIX_ENV: "development",
        RADIX_DATA_DIR: "data/private/e2e",
        RADIX_AUTH_MODE: "local",
        RADIX_STORAGE_MODE: "local",
        RADIX_ALLOWED_ORIGIN: "http://127.0.0.1:5179",
        RADIX_ALLOWED_ORIGINS: "",
        RADIX_DOCUMENT_STORAGE_MODE: "local",
        RADIX_LLM_MODE: "rules",
        RADIX_LLM_API_KEY: "",
        GROQ_API_KEY: "",
      },
    },
    {
      command: "npm run dev -- --port 5179",
      url: "http://127.0.0.1:5179",
      reuseExistingServer: false,
      env: {
        RADIX_API_TARGET: "http://127.0.0.1:8123",
        VITE_API_BASE_URL: "",
        VITE_SUPABASE_URL: "",
        VITE_SUPABASE_PUBLISHABLE_KEY: "",
      },
    },
  ],
});
