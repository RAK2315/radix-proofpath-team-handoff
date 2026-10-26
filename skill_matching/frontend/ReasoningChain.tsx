import type { Skill } from "../../shared/contracts/types";
import { useWorkspace } from "../../shared/ui/context";

/** Feature-owned interpretation of a matching decision; quotes come from its frozen inputs. */
export default function ReasoningChain({
  decision,
  onExplore,
}: {
  decision: any;
  onExplore: () => void;
}) {
  const w = useWorkspace();
  if (!decision?.jd_evidence) return null;
  const jd: Skill = decision.jd_evidence;
  const candidate: Skill | null = decision.candidate_evidence || null;
  const unresolved = decision.decision_type === "unresolved";
  return (
    <section className="reasoning-chain" aria-label="ProofPath reasoning chain">
      <p className="fine-print">
        Source → reviewed claim → contribution → next action
      </p>
      <ol>
        <li>
          <h3>1. What the job asks for</h3>
          <blockquote>
            {jd.evidence || "No source quote available for this requirement."}
          </blockquote>
          <p className="fine-print">
            {jd.source_file || "Manual JD entry"}
            {jd.source_page ? ` · page ${jd.source_page}` : ""} ·{" "}
            {decision.requirement_type}
          </p>
          <button className="text-button" onClick={() => w.showEvidence(jd)}>
            Open JD source
          </button>
        </li>
        <li>
          <h3>2. What the candidate claims</h3>
          {candidate ? (
            <>
              <blockquote>{candidate.evidence}</blockquote>
              <p className="fine-print">
                {candidate.source_file || "Manual claim"} ·{" "}
                {candidate.verification_status} · extraction confidence{" "}
                {candidate.confidence}
              </p>
              <button
                className="text-button"
                onClick={() => w.showEvidence(candidate)}
              >
                Open candidate source
              </button>
            </>
          ) : (
            <p>
              {unresolved
                ? "The wording or claim needs review before an equivalent claim can contribute."
                : "No equivalent reviewed claim was found in this profile. This is an evidence gap, not proof of missing ability."}
            </p>
          )}
        </li>
        <li>
          <h3>3. Why this affects the result</h3>
          <p>{decision.reason}</p>
          <p className="chain-points">
            {decision.score_contribution == null
              ? "Contribution unavailable"
              : `${decision.score_contribution.toFixed(2)} points out of 100`}
          </p>
          <p className="fine-print">
            This is this decision's share of weighted group coverage.
            Alternatives and AND groups are calculated together; group totals
            are in the report.
          </p>
        </li>
        <li>
          <h3>4. Choose a next step</h3>
          <p>
            {decision.recommended_action ||
              "Review the source before deciding on an action."}
          </p>
          <p className="fine-print">
            Adding supporting evidence does not increase a competency level. If
            you can demonstrate this requirement, review the real profile; if
            you need to learn it, treat that as capability development.
          </p>
          {!unresolved && !candidate && (
            <>
              <button className="button primary" onClick={onExplore}>
                Explore in Career GPS
              </button>
              <p className="fine-print">
                Select {decision.skill_name} in the hypothetical workspace. Your
                saved profile stays unchanged.
              </p>
            </>
          )}
        </li>
      </ol>
    </section>
  );
}
