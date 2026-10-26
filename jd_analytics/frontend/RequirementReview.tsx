import { Plus, Trash2 } from "lucide-react";
import type { Requirement, Skill } from "../../shared/contracts/types";

export default function RequirementReview({
  groups,
  skills,
  onChange,
  onEvidence,
}: {
  groups: Requirement[];
  skills: Skill[];
  onChange: (groups: Requirement[]) => void;
  onEvidence?: (group: Requirement) => void;
}) {
  const edit = (id: string, patch: Partial<Requirement>) =>
    onChange(
      groups.map((group) =>
        group.requirement_id === id ? { ...group, ...patch } : group,
      ),
    );
  return (
    <>
      <div className="section-heading">
        <h3>Requirement importance & alternatives</h3>
        <button
          className="button small"
          disabled={!skills.length}
          onClick={() =>
            onChange([
              ...groups,
              {
                requirement_id: crypto.randomUUID(),
                skill_ids: [skills[0].skill_id],
                operator: "AND",
                requirement_type: "unspecified",
                requires_review: false,
                evidence: "",
                source_page: null,
              },
            ])
          }
        >
          <Plus size={13} /> Add group
        </button>
      </div>
      <p className="fine-print">
        Mandatory groups weigh 2; other groups weigh 1. AND requires every
        member; OR needs any member. Ungrouped skills count as individual
        requirements. These are team heuristics.
      </p>
      {groups.map((group, index) => (
        <div key={group.requirement_id} className="requirement-group">
          {group.evidence && onEvidence && (
            <button className="evidence-link" onClick={() => onEvidence(group)}>
              Inspect requirement wording and source
            </button>
          )}
          {group.requires_review && (
            <div className="notice">
              This wording mixes alternatives and conjunctions. Edit the
              members/operator, then confirm its meaning.
            </div>
          )}
          <div className="requirement-edit">
            <span>
              {group.skill_ids
                .map(
                  (id) =>
                    skills.find((skill) => skill.skill_id === id)?.skill_name,
                )
                .join(` ${group.operator.toLowerCase()} `)}
            </span>
            <select
              aria-label={`Requirement ${index + 1} importance`}
              value={group.requirement_type}
              onChange={(event) =>
                edit(group.requirement_id, {
                  requirement_type: event.target
                    .value as Requirement["requirement_type"],
                })
              }
            >
              <option value="mandatory">Mandatory · 2×</option>
              <option value="preferred">Preferred · 1×</option>
              <option value="unspecified">Unspecified · 1×</option>
            </select>
            <select
              aria-label={`Requirement ${index + 1} operator`}
              value={group.operator}
              onChange={(event) =>
                edit(group.requirement_id, {
                  operator: event.target.value as Requirement["operator"],
                })
              }
            >
              <option>AND</option>
              <option>OR</option>
            </select>
            <button
              className="icon-button"
              aria-label={`Remove requirement group ${index + 1}`}
              onClick={() =>
                onChange(
                  groups.filter(
                    (item) => item.requirement_id !== group.requirement_id,
                  ),
                )
              }
            >
              <Trash2 size={14} />
            </button>
          </div>
          <label className="check">
            <input
              type="checkbox"
              checked={!group.requires_review}
              onChange={(event) =>
                edit(group.requirement_id, {
                  requires_review: !event.target.checked,
                })
              }
            />{" "}
            Group meaning reviewed
          </label>
          <details>
            <summary>Edit group members</summary>
            <div className="group-members">
              {skills.map((skill) => (
                <label className="check" key={skill.skill_id}>
                  <input
                    type="checkbox"
                    checked={group.skill_ids.includes(skill.skill_id)}
                    disabled={
                      group.skill_ids.length === 1 &&
                      group.skill_ids[0] === skill.skill_id
                    }
                    onChange={(event) =>
                      edit(group.requirement_id, {
                        skill_ids: event.target.checked
                          ? [...group.skill_ids, skill.skill_id]
                          : group.skill_ids.filter(
                              (id) => id !== skill.skill_id,
                            ),
                      })
                    }
                  />
                  {skill.skill_name}
                </label>
              ))}
            </div>
          </details>
        </div>
      ))}
    </>
  );
}
