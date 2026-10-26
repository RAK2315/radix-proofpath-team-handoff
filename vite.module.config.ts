import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";
const pages: Record<string, string> = {
  jd_analytics: "JDAnalyticsPage",
  resume_parsing: "ResumeParsingPage",
  profile_builder: "ProfileBuilderPage",
  talent_check: "TalentCheckPage",
  skill_matching: "SkillMatchingPage",
};
const selected = process.env.RADIX_MODULE || "jd_analytics";
if (!pages[selected]) throw new Error("Invalid RADIX_MODULE");
export default defineConfig({
  root: resolve("apps/module-web"),
  envDir: resolve("."),
  plugins: [react()],
  define: {
    "import.meta.env.VITE_HANDOFF_MODULE": JSON.stringify(selected),
    "import.meta.env.VITE_API_BASE_URL": JSON.stringify("/api"),
    "import.meta.env.VITE_SUPABASE_URL": JSON.stringify(""),
    "import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY": JSON.stringify(""),
  },
  resolve: {
    alias: {
      "@selected-module": resolve(
        selected,
        "frontend",
        pages[selected] + ".tsx",
      ),
      "@selected-evidence":
        selected === "skill_matching"
          ? resolve("skill_matching/frontend/ReasoningChain.tsx")
          : resolve("apps/module-web/NoEvidence.tsx"),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: { allow: [resolve(".")] },
    proxy: { "/api": process.env.RADIX_API_TARGET || "http://127.0.0.1:8000" },
  },
  build: { outDir: resolve("dist-module", selected), emptyOutDir: true },
});
