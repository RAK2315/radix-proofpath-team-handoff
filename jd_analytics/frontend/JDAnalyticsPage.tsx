import RequirementReview from "./RequirementReview";
import PasteJD from "./PasteJD";
import { useUnsavedChanges, confirmDiscard } from "../../shared/ui/drafts";
import { useEffect, useState } from "react";
import { Check, Save } from "lucide-react";
import type { Extraction } from "../../shared/contracts/types";
import { api } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import {
  Empty,
  NextButton,
  Notice,
  PageTitle,
  SkillEditor,
  UploadBox,
} from "../../shared/ui/components";

export default function JDAnalyticsPage() {
  const w = useWorkspace();
  const [draft, setDraft] = useState<Extraction | null>(w.jd);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [inputMode, setInputMode] = useState<"file" | "text">("file");
  useUnsavedChanges("jd", dirty);
  useEffect(() => {
    setDraft(w.jd);
    setDirty(false);
  }, [w.jd]);
  const edit = (patch: Partial<Extraction>) => {
    setDraft(draft ? { ...draft, ...patch } : draft);
    setDirty(true);
  };
  async function save() {
    if (!draft) return;
    setBusy(true);
    setError("");
    try {
      const value = await api<Extraction>(`/jd/${draft.id}`, {
        method: "PATCH",
        body: JSON.stringify({ ...draft, review_status: "reviewed" }),
      });
      w.cacheExtraction(value);
      w.selectJD(value.id);
      setDraft(value);
      setDirty(false);
      await w
        .refresh()
        .catch(() =>
          w.notify(
            "JD saved. Workspace refresh failed; your saved review is retained.",
          ),
        );
      w.notify("JD reviewed and saved. Matching now uses this revision.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="01 / UNDERSTAND THE OPPORTUNITY"
        title="Decode the job."
        description="Turn a job description into clear requirements, with the source behind every skill."
      />
      <section className="card">
        <div className="section-heading">
          <h2>Start with a job description</h2>
          <div
            className="segmented"
            role="tablist"
            aria-label="JD input method"
          >
            <button
              role="tab"
              aria-selected={inputMode === "file"}
              className={inputMode === "file" ? "selected" : ""}
              onClick={() => {
                if (confirmDiscard("pasted-jd")) setInputMode("file");
              }}
            >
              Upload file
            </button>
            <button
              role="tab"
              aria-selected={inputMode === "text"}
              className={inputMode === "text" ? "selected" : ""}
              onClick={() => setInputMode("text")}
            >
              Paste text
            </button>
          </div>
        </div>
        {inputMode === "text" ? (
          <PasteJD
            onResult={async (value) => {
              if (!confirmDiscard("jd")) return;
              setDraft(value);
              w.cacheExtraction(value);
              w.selectJD(value.id);
              await w
                .refresh()
                .catch(() =>
                  w.notify(
                    "JD extracted and retained. Retry workspace refresh when connected.",
                  ),
                );
            }}
          />
        ) : (
          <UploadBox
            endpoint="/jd/extract"
            onResult={async (value: Extraction) => {
              if (!confirmDiscard("jd")) return;
              w.cacheExtraction(value);
              w.selectJD(value.id);
              setDraft(value);
              await w
                .refresh()
                .catch(() =>
                  w.notify(
                    "JD extracted and retained. Retry workspace refresh when connected.",
                  ),
                );
            }}
          />
        )}
      </section>
      {error && <Notice tone="error">{error}</Notice>}
      {draft ? (
        <>
          <section className="card">
            <div className="section-heading">
              <div>
                <div className="eyebrow">{draft.source_file}</div>
                <h2>Review the requirements</h2>
              </div>
              <span className="pill">
                {draft.skills.length} skills · revision {draft.revision}
              </span>
            </div>
            <div className="form-grid">
              <label>
                Company
                <input
                  value={draft.company || ""}
                  onChange={(e) => edit({ company: e.target.value })}
                />
              </label>
              <label>
                Role
                <input
                  value={draft.role || ""}
                  onChange={(e) => edit({ role: e.target.value })}
                />
              </label>
            </div>
            <p className="fine-print" role="status">
              {draft.llm_status === "processed"
                ? `LLM processed · ${draft.model_version} · source review required`
                : draft.llm_status === "unavailable"
                  ? "Model unavailable · rules-only fallback"
                  : "Rules-only extraction · human review required"}
            </p>
            {draft.llm_status === "processed" &&
              draft.skills.some(
                (skill) => skill.claim_status === "needs_review",
              ) && (
                <button
                  className="button"
                  onClick={() =>
                    edit({
                      skills: draft.skills.map((skill) => ({
                        ...skill,
                        claim_status: "claimed" as const,
                      })),
                    })
                  }
                >
                  I checked all source claims — confirm them
                </button>
              )}
            {draft.warnings.map((x) => (
              <Notice key={x}>{x}</Notice>
            ))}
            {draft.warnings.some((x) =>
              x.startsWith("Requirement not fully parsed;"),
            ) && (
              <section className="unparsed-review">
                <h3>Check missing requirements before scoring</h3>
                <p className="fine-print">
                  Compare the source lines above with the skill list. Add any
                  missing skills and repair the groups. Acknowledge only after
                  checking coverage; saving alone keeps this match provisional.
                </p>
                <button
                  className="button"
                  onClick={() =>
                    edit({
                      warnings: draft.warnings.filter(
                        (x) => !x.startsWith("Requirement not fully parsed;"),
                      ),
                    })
                  }
                >
                  I reviewed and corrected requirement coverage
                </button>
              </section>
            )}
            <SkillEditor
              skills={draft.skills}
              onChange={(skills) => {
                const ids = new Set(skills.map((s) => s.skill_id));
                edit({
                  skills,
                  requirement_groups: draft.requirement_groups
                    .map((g) => ({
                      ...g,
                      skill_ids: g.skill_ids.filter((id) => ids.has(id)),
                    }))
                    .filter((g) => g.skill_ids.length),
                });
              }}
            />
            <RequirementReview
              groups={draft.requirement_groups}
              skills={draft.skills}
              onChange={(requirement_groups) => edit({ requirement_groups })}
              onEvidence={(group) =>
                w.showEvidence({
                  skill_name: "Requirement source",
                  evidence: group.evidence,
                  source_page: group.source_page,
                  source_file: draft.source_file,
                  source_document_id: draft.document_id,
                  source_type: "document",
                  confidence: "medium",
                })
              }
            />
            <div className="card-footer">
              <span className="muted">
                {dirty
                  ? "Unsaved review changes"
                  : draft.review_status === "reviewed"
                    ? "Reviewed · ready for matching"
                    : "Review extraction before continuing"}
              </span>
              <button
                className="button primary"
                disabled={busy}
                onClick={() => void save()}
              >
                {draft.review_status === "reviewed" ? (
                  <Save size={16} />
                ) : (
                  <Check size={16} />
                )}{" "}
                {busy ? "Saving…" : "Save reviewed JD"}
              </button>
            </div>
          </section>
          <div className="next-step">
            <p>
              {w.profile
                ? "Your candidate is saved. Continue to your specific job comparison."
                : "Next, bring your experience into the picture."}
            </p>
            <NextButton
              onClick={() => w.navigate(w.profile ? "matching" : "resume")}
            >
              {w.profile ? "See your JD match" : "Parse your resume"}
            </NextButton>
          </div>
        </>
      ) : (
        <Empty
          title="The right match starts with the right requirements."
          description="Upload a JD above, or choose a previously saved job from the workspace selectors."
        />
      )}
    </>
  );
}
