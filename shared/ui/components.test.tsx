import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Drawer, Score, SkillEditor } from "./components";
import { WorkspaceContext } from "./context";
import type { Workspace } from "./context";
import { manualSkill } from "../contracts/types";

const workspace = {
  showEvidence: vi.fn(),
  notify: vi.fn(),
} as unknown as Workspace;
describe("generic evidence and score display", () => {
  it("filters detailed families without changing competency categories or claims", () => {
    const change = vi.fn();
    const skills = Array.from({ length: 10 }, (_, i) => ({
      ...manualSkill(`Skill ${i}`),
      skill_family: i === 9 ? "Machine Learning" : "Programming Languages",
      category_code: "COD" as const,
    }));
    render(
      <WorkspaceContext.Provider value={workspace}>
        <SkillEditor skills={skills} onChange={change} />
      </WorkspaceContext.Provider>,
    );
    expect(screen.getAllByLabelText("Skill name")).toHaveLength(8);
    fireEvent.click(screen.getByRole("button", { name: "Show all 10 skills" }));
    expect(screen.getAllByLabelText("Skill name")).toHaveLength(10);
    fireEvent.change(screen.getByLabelText("Filter skill family"), {
      target: { value: "Machine Learning" },
    });
    expect(screen.getAllByLabelText("Skill name")).toHaveLength(1);
    expect(screen.getByLabelText("Skill name")).toHaveValue("Skill 9");
    expect(change).not.toHaveBeenCalled();
    expect(skills[9].category_code).toBe("COD");
  });
  it("shows unknown rather than zero", () => {
    render(<Score value={null} label="Readiness" />);
    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.queryByText("0.0")).not.toBeInTheDocument();
  });
  it("renders category evidence arrays and lets the user drill into a claim", () => {
    const skill = manualSkill("SQL");
    render(
      <WorkspaceContext.Provider value={workspace}>
        <Drawer
          value={{
            category_name: "SQL",
            category_code: "SQL",
            required_level: 8,
            candidate_level: 4,
            contribution: 4.1667,
            evidence: [skill],
          }}
          onClose={() => {}}
        />
      </WorkspaceContext.Provider>,
    );
    fireEvent.click(screen.getByRole("button", { name: /SQL/ }));
    expect(workspace.showEvidence).toHaveBeenCalledWith(skill);
  });
  it("keeps manual edits separate from document support", () => {
    const change = vi.fn();
    const skill = {
      ...manualSkill("SQL"),
      source_type: "document" as const,
      source_document_id: "synthetic-id",
    };
    render(
      <WorkspaceContext.Provider value={workspace}>
        <SkillEditor skills={[skill]} onChange={change} />
      </WorkspaceContext.Provider>,
    );
    fireEvent.change(screen.getByLabelText("Skill name"), {
      target: { value: "PostgreSQL" },
    });
    expect(change.mock.calls[0][0][0]).toMatchObject({
      source_type: "manual",
      source_document_id: null,
    });
  });
});
