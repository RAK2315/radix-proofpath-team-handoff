import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const key = env.VITE_SUPABASE_PUBLISHABLE_KEY || "";
  let role = "";
  try {
    role =
      JSON.parse(Buffer.from(key.split(".")[1], "base64url").toString()).role ||
      "";
  } catch {
    /* Publishable keys are not JWTs. */
  }
  if (key.startsWith("sb_secret_") || role === "service_role")
    throw new Error(
      "A privileged Supabase key must never be included in the frontend",
    );
  if (
    process.env.VERCEL === "1" &&
    (!env.VITE_API_BASE_URL?.startsWith("https://") ||
      !env.VITE_SUPABASE_URL?.startsWith("https://") ||
      !key)
  )
    throw new Error(
      "Vercel requires HTTPS VITE_API_BASE_URL, VITE_SUPABASE_URL and a publishable key",
    );
  return {
    plugins: [react()],
    server: {
      port: 5173,
      strictPort: true,
      // Windows editors/formatters can briefly truncate files before finishing a save.
      // Wait for writes to settle so the long-running server never caches an empty module.
      watch: {
        awaitWriteFinish: { stabilityThreshold: 250, pollInterval: 50 },
      },
      proxy: {
        "/api": process.env.RADIX_API_TARGET || "http://127.0.0.1:8000",
      },
    },
    build: { outDir: "dist" },
    test: {
      environment: "jsdom",
      include: ["**/*.test.ts", "**/*.test.tsx"],
      exclude: [
        "node_modules/**",
        ".venv/**",
        "verification/**",
        "docs/internal/**",
      ],
      setupFiles: ["./tests/frontend/setup.ts"],
    },
  };
});
