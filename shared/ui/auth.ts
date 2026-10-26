import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
export const authClient =
  url && key
    ? createClient(url, key, {
        auth: {
          storage: sessionStorage,
          storageKey: "proofpath-auth-session",
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: false,
        },
      })
    : null;

export async function accessToken(): Promise<string | null> {
  if (!authClient) return sessionStorage.getItem("proofpath-token");
  const { data, error } = await authClient.auth.getSession();
  if (error)
    throw new Error("Your session needs to be refreshed. Sign in again.");
  return data.session?.access_token || null;
}

export function clearWorkspaceSelection() {
  for (const key of [
    "profile-id",
    "jd-id",
    "resume-id",
    "company-id",
    "benchmark-mode",
    "proofpath-token",
  ])
    sessionStorage.removeItem(key);
}
