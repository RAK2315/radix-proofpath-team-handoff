import { useEffect, useRef } from "react";
import { ArrowUpRight, Download, FileText, X } from "lucide-react";
import type { Skill } from "../contracts/types";
import { useWorkspace } from "./context";
import { apiResponse } from "./api";

export default function EvidenceDrawer({
  value,
  onClose,
  children,
}: {
  value: any;
  onClose: () => void;
  children?: React.ReactNode;
}) {
  const panel = useRef<HTMLElement>(null);
  const { showEvidence, notify } = useWorkspace();
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    panel.current?.querySelector<HTMLButtonElement>("button")?.focus();
    const trap = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
      if (event.key !== "Tab") return;
      const nodes = Array.from(
        panel.current?.querySelectorAll<HTMLElement>(
          'button,a[href],input,select,textarea,summary,[tabindex="0"]',
        ) || [],
      );
      const first = nodes[0],
        last = nodes[nodes.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", trap);
    return () => {
      document.removeEventListener("keydown", trap);
      previous?.focus();
    };
  }, [onClose]);
  async function download() {
    try {
      const response = await apiResponse(
        `/documents/${value.source_document_id}/download`,
      );
      if (!response.ok) throw new Error("Source is unavailable or expired.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = value.source_file || "source";
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      notify((error as Error).message);
    }
  }
  const isSkill = typeof value?.evidence === "string";
  const related: Skill[] = Array.isArray(value?.evidence)
    ? value.evidence
    : [value?.jd_evidence, value?.candidate_evidence].filter(Boolean);
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        ref={panel}
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Evidence and decision receipt"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="section-bar">
          <div className="eyebrow">PROOFPATH / SOURCE EXPLORER</div>
          <button
            className="icon-button"
            aria-label="Close evidence"
            onClick={onClose}
          >
            <X />
          </button>
        </div>
        <h2>
          {value?.skill_name || value?.category_name || "Decision receipt"}
        </h2>
        {children}
        {isSkill ? (
          <>
            <div className="evidence-quote">“{value.evidence}”</div>
            <dl>
              <dt>Source</dt>
              <dd>
                {value.source_file || "Manual entry"}{" "}
                {value.source_page ? `· page ${value.source_page}` : ""}
              </dd>
              <dt>Claim origin</dt>
              <dd>{value.source_type}</dd>
              <dt>Extraction confidence</dt>
              <dd>{value.confidence}</dd>
              <dt>Verification</dt>
              <dd>Unverified claim</dd>
              <dt>Claim review</dt>
              <dd>
                {value.claim_status === "needs_review"
                  ? "Needs review before matching"
                  : "Claimed; ability remains unverified"}
              </dd>
            </dl>
            {value.source_document_id && (
              <button className="button" onClick={() => void download()}>
                <Download size={15} /> Download original source
              </button>
            )}
            <div className="notice">
              A document supports that a claim was made. It does not
              independently verify ability or authorship.
            </div>
          </>
        ) : (
          <>
            {!children && value?.reason && <p>{value.reason}</p>}
            {!children && value?.score_contribution != null && (
              <div className="notice">
                <strong>Score contribution</strong>
                <br />
                {value.score_contribution.toFixed(2)} points out of 100 for this
                decision.
              </div>
            )}
            {!children && value?.recommended_action && (
              <div className="notice">
                <strong>Recommended action</strong>
                <br />
                {value.recommended_action}
              </div>
            )}
            {value?.category_code && value?.required_level != null && (
              <dl>
                <dt>Self-reported level</dt>
                <dd>{value.candidate_level ?? "Unknown"}</dd>
                <dt>Company expectation</dt>
                <dd>{value.required_level}</dd>
                <dt>Score contribution</dt>
                <dd>
                  {value.contribution == null
                    ? "Awaiting assessment"
                    : `${value.contribution} points out of 100`}
                </dd>
                <dt>Shortfall</dt>
                <dd>{value.shortfall ?? "Unknown"}</dd>
              </dl>
            )}
            {!children &&
              related.map((skill, index) => (
                <button
                  className="decision-row"
                  key={`${skill.skill_id}-${index}`}
                  onClick={() => showEvidence(skill)}
                >
                  <FileText size={17} />
                  <div>
                    <strong>{skill.skill_name}</strong>
                    <p>
                      {skill.source_file || skill.source_type} ·{" "}
                      {skill.evidence_type}
                    </p>
                  </div>
                  <ArrowUpRight size={15} />
                </button>
              ))}
          </>
        )}
        <details open={!isSkill && !children}>
          <summary>Inspect complete record</summary>
          <pre>{JSON.stringify(value, null, 2)}</pre>
        </details>
      </aside>
    </div>
  );
}
