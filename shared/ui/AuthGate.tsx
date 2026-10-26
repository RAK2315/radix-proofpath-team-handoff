import { createContext, useContext, useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { api } from "./api";
import { authClient, clearWorkspaceSelection } from "./auth";

const AuthContext = createContext<{
  email: string;
  signOut?: () => Promise<void>;
}>({ email: "" });
export const useAuth = () => useContext(AuthContext);

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState("");
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    void api("/status")
      .then((status) => {
        if (active) {
          setMode(status.auth_mode);
          setError("");
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [retry]);
  useEffect(() => {
    if (!authClient) {
      setReady(true);
      return;
    }
    const { data } = authClient.auth.onAuthStateChange((_event, next) => {
      const previous = sessionStorage.getItem("proofpath-owner");
      if (previous !== (next?.user.id || "")) clearWorkspaceSelection();
      sessionStorage.setItem("proofpath-owner", next?.user.id || "");
      setSession(next);
      setReady(true);
    });
    return () => data.subscription.unsubscribe();
  }, []);
  async function signOut() {
    // Clear candidate UI immediately, even if remote sign-out fails offline.
    clearWorkspaceSelection();
    setSession(null);
    const { error } = await authClient!.auth.signOut({ scope: "local" });
    if (error) {
      sessionStorage.removeItem("proofpath-auth-session");
      setError(
        "Signed out of this workspace. Remote session revocation was unavailable.",
      );
    }
  }
  if (mode === "local") return children;
  if (mode === "supabase" && ready && session)
    return (
      <AuthContext.Provider
        key={session.user.id}
        value={{ email: session.user.email || "", signOut }}
      >
        {children}
      </AuthContext.Provider>
    );
  return (
    <main className="auth-screen">
      <section className="card auth-card">
        <div className="eyebrow">RADIX / PROOFPATH</div>
        <h1>{mode ? "Your private workspace." : "Connecting to ProofPath…"}</h1>
        {mode === "supabase" && authClient && (
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              setBusy(true);
              setError("");
              try {
                const { error } = await authClient!.auth.signInWithPassword({
                  email,
                  password,
                });
                if (error) throw error;
                setPassword("");
              } catch {
                setError(
                  "Sign-in failed. Check your credentials and connection, then retry.",
                );
              } finally {
                setBusy(false);
              }
            }}
          >
            <p>
              Sign in with the account provided by your team. Candidate
              documents stay separate for each account.
            </p>
            <label>
              Email
              <input
                type="email"
                autoComplete="username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>
            <button className="button primary" disabled={busy}>
              {busy ? "Signing in…" : "Sign in"}
            </button>
          </form>
        )}
        {mode === "supabase" && !authClient && (
          <p role="alert">
            Cloud sign-in is not configured. Set VITE_SUPABASE_URL and
            VITE_SUPABASE_PUBLISHABLE_KEY, then rebuild the frontend.
          </p>
        )}
        {error && <p role="alert">{error}</p>}
        {!mode && error && (
          <button className="button" onClick={() => setRetry(retry + 1)}>
            Retry connection
          </button>
        )}
      </section>
    </main>
  );
}
