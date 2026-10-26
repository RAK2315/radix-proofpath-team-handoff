import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { WorkspaceContext } from "../../shared/ui/context";
import { workspace } from "../../tests/frontend/workspace";
import ProfileBuilderPage from "./ProfileBuilderPage";
it("supports all twelve self-ratings with unknown defaults and validates empty names", () => {
  render(
    <WorkspaceContext.Provider value={workspace()}>
      <ProfileBuilderPage />
    </WorkspaceContext.Provider>,
  );
  expect(screen.getByRole("button", { name: "Save profile" })).toBeDisabled();
  expect(screen.getByText(/0\/12 assessed/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Full name"), {
    target: { value: "Synthetic Candidate" },
  });
  expect(screen.getByRole("button", { name: "Save profile" })).toBeEnabled();
  fireEvent.change(screen.getByLabelText("COD competency"), {
    target: { value: "5" },
  });
  expect(screen.getByText(/1\/12 assessed/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("education"), {
    target: { value: "Synthetic degree\n" },
  });
  expect(screen.getByLabelText("education")).toHaveValue("Synthetic degree\n");
});
