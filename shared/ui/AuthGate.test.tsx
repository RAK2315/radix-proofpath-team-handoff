import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
const state = vi.hoisted(() => ({ listener: null as any, signedIn: false }));
vi.mock("./api", () => ({
  api: vi.fn().mockResolvedValue({ auth_mode: "supabase" }),
}));
vi.mock("./auth", () => ({
  clearWorkspaceSelection: vi.fn(() => sessionStorage.removeItem("profile-id")),
  authClient: {
    auth: {
      onAuthStateChange: vi.fn((callback: any) => {
        state.listener = callback;
        callback("INITIAL_SESSION", null);
        return { data: { subscription: { unsubscribe: vi.fn() } } };
      }),
      signInWithPassword: vi.fn(async () => {
        state.listener("SIGNED_IN", {
          user: { id: "synthetic-user", email: "synthetic@example.test" },
        });
        return { error: null };
      }),
      signOut: vi.fn().mockResolvedValue({ error: null }),
    },
  },
}));
import AuthGate, { useAuth } from "./AuthGate";
function PrivateWorkspace() {
  const auth = useAuth();
  return (
    <div>
      Private candidate workspace
      <button onClick={() => void auth.signOut?.()}>Sign out</button>
    </div>
  );
}
it("gates private content behind sign-in and unmounts it on sign-out", async () => {
  render(
    <AuthGate>
      <PrivateWorkspace />
    </AuthGate>,
  );
  expect(
    screen.queryByText("Private candidate workspace"),
  ).not.toBeInTheDocument();
  await screen.findByRole("button", { name: "Sign in" });
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "synthetic@example.test" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "synthetic-password" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
  await screen.findByText("Private candidate workspace");
  sessionStorage.setItem("profile-id", "private-selection");
  fireEvent.click(screen.getByRole("button", { name: "Sign out" }));
  await waitFor(() =>
    expect(
      screen.queryByText("Private candidate workspace"),
    ).not.toBeInTheDocument(),
  );
  expect(sessionStorage.getItem("profile-id")).toBeNull();
});
