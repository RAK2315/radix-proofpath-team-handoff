import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { WorkspaceContext } from "../../shared/ui/context";
import { syntheticProfile, workspace } from "../../tests/frontend/workspace";
import SkillMatchingPage from "./SkillMatchingPage";
it("requires a specific saved job, independently of profile competency", () => {
  const context = workspace({ profile: syntheticProfile() });
  render(
    <WorkspaceContext.Provider value={context}>
      <SkillMatchingPage />
    </WorkspaceContext.Provider>,
  );
  expect(
    screen.getByRole("button", { name: "Analyze this match" }),
  ).toBeDisabled();
  fireEvent.click(screen.getByRole("button", { name: "Add a JD" }));
  expect(context.navigate).toHaveBeenCalledWith("jd");
});
