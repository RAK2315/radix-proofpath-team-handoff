import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { WorkspaceContext } from "../../shared/ui/context";
import { syntheticProfile, workspace } from "../../tests/frontend/workspace";
import TalentCheckPage from "./TalentCheckPage";
it("makes missing real benchmarks explicit and lab exploration opt-in", () => {
  const context = workspace({ profile: syntheticProfile() });
  render(
    <WorkspaceContext.Provider value={context}>
      <TalentCheckPage />
    </WorkspaceContext.Provider>,
  );
  expect(
    screen.getByRole("button", { name: "Run Talent Check" }),
  ).toBeDisabled();
  expect(
    screen.getByText("Connect the company benchmark source."),
  ).toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", {
      name: "Explore explicitly synthetic lab data",
    }),
  );
  expect(context.setMode).toHaveBeenCalledWith("synthetic");
});
