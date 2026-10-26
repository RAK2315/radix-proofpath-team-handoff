import { useEffect, useState } from "react";
import type { Extraction } from "../../shared/contracts/types";
import { api } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import { useUnsavedChanges, confirmDiscard } from "../../shared/ui/drafts";
import {
  Empty,
  NextButton,
  Notice,
  PageTitle,
  SkillEditor,
  UploadBox,
} from "../../shared/ui/components";
export default function ResumeParsingPage() {
  const w = useWorkspace();
  const [draft, setDraft] = useState<Extraction | null>(w.resume);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useUnsavedChanges(
    "resume",
    Boolean(draft && JSON.stringify(draft) !== JSON.stringify(w.resume)),
  );
  useEffect(() => {
    setDraft(w.resume);
  }, [w.resume]);
  async function save() {
    if (!draft) return;
    setBusy(true);
    setError("");
    try {
      const result = await api<Extraction>(`/resumes/${draft.id}`, {
        method: "PATCH",
        body: JSON.stringify({ ...draft, review_status: "reviewed" }),
      });
      w.cacheExtraction(result);
      w.selectResume(result.id);
      setDraft(result);
      await w
        .refresh()
        .catch(() =>
          w.notify(
            "Resume review saved and retained. Workspace refresh failed.",
          ),
        );
      w.notify("Resume review saved. Import it from Profile Builder.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="02 / FIND YOUR SIGNAL"
        action={
          <select
            aria-label="Selected resume"
            value={w.resume?.id || ""}
            onChange={(e) => {
              if (confirmDiscard("resume")) w.selectResume(e.target.value);
            }}
          >
            <option value="">Choose saved resume</option>
            {w.resumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.name || resume.source_file}
              </option>
            ))}
          </select>
        }
        title="Experience, unpacked."
        description="Extract what your resume says. Review what it means. Keep every claim connected to its source."
      />
      <section className="card">
        <div className="section-heading">
          <h2>Upload your resume</h2>
          <span className="pill">Private workspace</span>
        </div>
        <UploadBox
          endpoint="/resumes/extract"
          onResult={async (value: Extraction) => {
            if (!confirmDiscard("resume")) return;
            w.cacheExtraction(value);
            w.selectResume(value.id);
            setDraft(value);
            await w
              .refresh()
              .catch(() =>
                w.notify(
                  "Resume extracted and retained. Retry workspace refresh when connected.",
                ),
              );
          }}
        />
        <p className="fine-print">
          Uploaded files expire after 7 days when document cleanup runs. Delete
          them anytime from Data & privacy. Profile claims remain editable.
        </p>
      </section>
      {error && <Notice tone="error">{error}</Notice>}
      {draft ? (
        <>
          <section className="card">
            <div className="section-heading">
              <div>
                <div className="eyebrow">{draft.source_file}</div>
                <h2>Review your extracted profile</h2>
              </div>
              <span className="pill">{draft.skills.length} skill claims</span>
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
                    setDraft({
                      ...draft,
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
            <div className="form-grid">
              <label>
                Name
                <input
                  value={draft.name}
                  onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={draft.email}
                  onChange={(e) =>
                    setDraft({ ...draft, email: e.target.value })
                  }
                />
              </label>
            </div>
            <SkillEditor
              skills={draft.skills}
              onChange={(skills) => setDraft({ ...draft, skills })}
            />
            <div className="form-grid">
              {(
                [
                  "education",
                  "projects",
                  "experience",
                  "certifications",
                  "internships",
                  "hackathons",
                  "achievements",
                ] as const
              ).map((field) => (
                <label key={field} className="capitalize">
                  {field}
                  <textarea
                    aria-label={`Extracted ${field}`}
                    rows={4}
                    value={draft[field].join("\n")}
                    onChange={(e) =>
                      setDraft({
                        ...draft,
                        [field]: e.target.value.split("\n"),
                      })
                    }
                  />
                </label>
              ))}
            </div>
            <div className="card-footer">
              <span className="muted">
                Document-supported claims · ability remains unverified
              </span>
              <button
                className="button primary"
                disabled={busy}
                onClick={() => void save()}
              >
                {busy ? "Saving…" : "Save reviewed resume"}
              </button>
            </div>
          </section>
          <div className="next-step">
            <p>Add the parts of your story that a resume misses.</p>
            <NextButton onClick={() => w.navigate("profile")}>
              Build your profile
            </NextButton>
          </div>
        </>
      ) : (
        <Empty
          title="Your experience is more than a keyword list."
          description="Upload a resume to extract skills, education, projects and technical experience."
        />
      )}
    </>
  );
}
