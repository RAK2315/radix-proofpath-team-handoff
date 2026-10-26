import { render, screen, fireEvent } from "@testing-library/react";
import { it, expect, vi } from "vitest";
import { WorkspaceContext } from "../../shared/ui/context";
import { manualSkill } from "../../shared/contracts/types";
import { workspace } from "../../tests/frontend/workspace";
import ReasoningChain from "./ReasoningChain";

it("shows actual quotes, contributions and origin without inventing candidate evidence", () => {
  const explore = vi.fn();
  const context = workspace();
  const jd = {
    ...manualSkill("Docker"),
    evidence: "Docker would be useful",
    source_file: "synthetic.txt",
  };
  render(
    <WorkspaceContext.Provider value={context}>
      <ReasoningChain
        decision={{
          jd_evidence: jd,
          skill_name: "Docker",
          candidate_evidence: null,
          score_contribution: 0,
          requirement_type: "preferred",
          decision_type: "missing",
          reason: "No equivalent claim",
          recommended_action: "Review and demonstrate Docker",
        }}
        onExplore={explore}
      />
    </WorkspaceContext.Provider>,
  );
  expect(screen.getByText("Docker would be useful")).toBeInTheDocument();
  expect(screen.getByText(/No equivalent reviewed claim/)).toBeInTheDocument();
  expect(screen.getByText("0.00 points out of 100")).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Open candidate source" }),
  ).not.toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: "Explore in Career GPS" }),
  );
  expect(explore).toHaveBeenCalled();
});
