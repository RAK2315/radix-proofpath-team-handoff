import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { WorkspaceContext } from "../../shared/ui/context";
import { extraction, workspace } from "../../tests/frontend/workspace";
import ResumeParsingPage from "./ResumeParsingPage";
it("keeps resume sections editable without inferring competency", () => {
  render(
    <WorkspaceContext.Provider
      value={workspace({ resume: extraction("resume") })}
    >
      <ResumeParsingPage />
    </WorkspaceContext.Provider>,
  );
  fireEvent.change(screen.getByLabelText("Extracted projects"), {
    target: { value: "Synthetic project with SQL\n" },
  });
  expect(screen.getByLabelText("Extracted projects")).toHaveValue(
    "Synthetic project with SQL\n",
  );
  expect(screen.getByText(/ability remains unverified/)).toBeInTheDocument();
  expect(screen.queryByLabelText("COD competency")).not.toBeInTheDocument();
});
