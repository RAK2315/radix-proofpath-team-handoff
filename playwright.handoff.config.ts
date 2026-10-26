import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";
const modules = [
  "jd_analytics",
  "resume_parsing",
  "profile_builder",
  "talent_check",
  "skill_matching",
];
const python = resolve(
  process.platform === "win32"
    ? ".venv/Scripts/python.exe"
    : ".venv/bin/python",
);
export default defineConfig({
  testDir: "tests/handoff",
  workers: 1,
  timeout: 60000,
  retries: 0,
  use: {
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: modules.map((name, i) => ({
    name,
    use: { baseURL: `http://127.0.0.1:${5310 + i}` },
  })),
  webServer: modules.flatMap(
    (
      name,
      i,
    ): {
      command: string;
      url: string;
      reuseExistingServer: boolean;
      env: Record<string, string>;
    }[] => [
      {
        command: `"${python}" -m uvicorn apps.api.standalone:app --host 127.0.0.1 --port ${8210 + i}`,
        url: `http://127.0.0.1:${8210 + i}/api/health`,
        reuseExistingServer: false,
        env: {
          RADIX_MODULE: name,
          RADIX_ENV: "development",
          RADIX_AUTH_MODE: "local",
          RADIX_STORAGE_MODE: "local",
          RADIX_DOCUMENT_STORAGE_MODE: "local",
          RADIX_LLM_MODE: "rules",
          RADIX_LLM_API_KEY: "",
          GROQ_API_KEY: "",
          RADIX_DATA_DIR: `data/private/handoff-browser-${name}`,
          RADIX_ALLOWED_ORIGINS: "",
          RADIX_ALLOWED_ORIGIN: `http://127.0.0.1:${5310 + i}`,
        },
      },
      {
        command: `npm run dev:module -- --host 127.0.0.1 --port ${5310 + i}`,
        url: `http://127.0.0.1:${5310 + i}`,
        reuseExistingServer: false,
        env: {
          RADIX_MODULE: name,
          RADIX_API_TARGET: `http://127.0.0.1:${8210 + i}`,
        },
      },
    ],
  ),
});
