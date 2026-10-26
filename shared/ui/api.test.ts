import { afterEach, expect, it, vi } from "vitest";
import { api, apiResponse, apiUrl } from "./api";
afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  sessionStorage.clear();
});
it("makes network failures actionable without discarding the draft", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
  );
  await expect(
    api("/profiles", { method: "POST", body: "{}" }),
  ).rejects.toMatchObject({
    code: "NETWORK_ERROR",
    message: expect.stringContaining("draft is still here"),
  });
});
it("uses the deployed API base for JSON and original-file downloads with a bearer session", async () => {
  vi.stubEnv("VITE_API_BASE_URL", "https://synthetic-api.hf.space/api/");
  sessionStorage.setItem("proofpath-token", "synthetic-jwt");
  const fetcher = vi.fn().mockResolvedValue(new Response("synthetic original"));
  vi.stubGlobal("fetch", fetcher);
  expect(apiUrl("/profiles")).toBe(
    "https://synthetic-api.hf.space/api/profiles",
  );
  await apiResponse("/documents/synthetic-id/download");
  expect(fetcher.mock.calls[0][0]).toBe(
    "https://synthetic-api.hf.space/api/documents/synthetic-id/download",
  );
  expect(fetcher.mock.calls[0][1].headers.Authorization).toBe(
    "Bearer synthetic-jwt",
  );
});
it("handles a non-JSON API outage with a useful fallback", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(new Response("Upstream unavailable", { status: 502 })),
  );
  await expect(api("/profiles")).rejects.toMatchObject({
    code: "HTTP_ERROR",
    message: expect.any(String),
  });
});
