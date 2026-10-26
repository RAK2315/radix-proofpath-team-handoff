import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { manualSkill } from "../../shared/contracts/types";
import { WorkspaceContext } from "../../shared/ui/context";
import { extraction, workspace } from "../../tests/frontend/workspace";
import JDAnalyticsPage from "./JDAnalyticsPage";
import RequirementReview from "./RequirementReview";

it("lets the reviewer correct extracted company and requirement groups", () => {
  const jd = extraction();
  render(
    <WorkspaceContext.Provider value={workspace({ jd })}>
      <JDAnalyticsPage />
    </WorkspaceContext.Provider>,
  );
  fireEvent.change(screen.getByLabelText("Company"), {
    target: { value: "Synthetic Company" },
  });
  expect(screen.getByLabelText("Company")).toHaveValue("Synthetic Company");
  expect(screen.getByText("Unsaved review changes")).toBeInTheDocument();
});
it("creates an explicit group from the reviewed skills", () => {
  const change = vi.fn();
  const skill = manualSkill("SQL");
  render(<RequirementReview skills={[skill]} groups={[]} onChange={change} />);
  fireEvent.click(screen.getByRole("button", { name: "Add group" }));
  expect(change.mock.calls[0][0][0].skill_ids).toEqual([skill.skill_id]);
});

it("offers paste text without removing file uploads", () => {
  render(
    <WorkspaceContext.Provider value={workspace()}>
      <JDAnalyticsPage />
    </WorkspaceContext.Provider>,
  );
  fireEvent.click(screen.getByRole("tab", { name: "Paste text" }));
  expect(
    screen.getByRole("button", { name: "Extract pasted JD" }),
  ).toBeDisabled();
  fireEvent.change(screen.getByLabelText("Job description text"), {
    target: { value: "Required: Python and SQL" },
  });
  expect(
    screen.getByRole("button", { name: "Extract pasted JD" }),
  ).toBeEnabled();
});

it("distinguishes LLM processing from fallback and requires human confirmation", () => {
  const jd = extraction();
  jd.llm_status = "processed";
  jd.model_version = "synthetic-mocked-model";
  jd.skills = [
    {
      ...manualSkill("Rust"),
      source_type: "document",
      claim_status: "needs_review",
    },
  ];
  render(
    <WorkspaceContext.Provider value={workspace({ jd })}>
      <JDAnalyticsPage />
    </WorkspaceContext.Provider>,
  );
  expect(screen.getByRole("status")).toHaveTextContent(
    "LLM processed · synthetic-mocked-model",
  );
  expect(screen.getByText(/Unreviewed claim/)).toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: /I checked all source claims/ }),
  );
  expect(screen.queryByText(/Unreviewed claim/)).not.toBeInTheDocument();
});
