import { useEffect, useState } from "react";
import { Download, Plus, Save, Trash2 } from "lucide-react";
import { blankProfile, categories } from "../../shared/contracts/types";
import type { Profile } from "../../shared/contracts/types";
import { api } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import { useUnsavedChanges, confirmDiscard } from "../../shared/ui/drafts";
import {
  NextButton,
  Notice,
  PageTitle,
  SkillEditor,
  UploadBox,
} from "../../shared/ui/components";
export default function ProfileBuilderPage() {
  const w = useWorkspace();
  const [draft, setDraft] = useState<Profile>(w.profile || blankProfile());
  const [saved, setSaved] = useState(Boolean(w.profile));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [replace, setReplace] = useState(false);
  const [dirty, setDirty] = useState(false);
  useUnsavedChanges("profile", dirty);
  useEffect(() => {
    setDraft(w.profile || blankProfile());
    setSaved(Boolean(w.profile));
    setDirty(false);
  }, [w.profile]);
  const edit = (patch: Partial<Profile>) => {
    setDraft({ ...draft, ...patch });
    setDirty(true);
  };
  async function importResume() {
    const r = w.resume;
    if (!r) return;
    setError("");
    try {
      const merged = await api<Profile>("/profiles/import-resume", {
        method: "POST",
        body: JSON.stringify({
          resume_id: r.id,
          profile: { ...draft, name: draft.name || r.name },
          replace_existing: replace,
        }),
      });
      setDraft(merged);
      setDirty(true);
      w.notify("Resume imported into this draft. Review and save to persist.");
    } catch (error) {
      setError((error as Error).message);
    }
  }
  async function save() {
    setBusy(true);
    setError("");
    try {
      const profile = await api<Profile>(
        saved ? `/profiles/${draft.id}` : "/profiles",
        { method: saved ? "PATCH" : "POST", body: JSON.stringify(draft) },
      );
      setDraft(profile);
      setSaved(true);
      setDirty(false);
      w.cacheProfile(profile);
      w.selectProfile(profile.id);
      await w
        .refresh()
        .catch(() =>
          w.notify(
            "Profile saved on the server. Refresh the page to update the workspace list.",
          ),
        );
      w.notify(
        "Profile saved. Previous evaluation receipts were invalidated on edits.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    try {
      await api(`/profiles/${draft.id}`, { method: "DELETE" });
      w.selectProfile("");
      await w.refresh();
      setDraft(blankProfile());
      setSaved(false);
      w.notify(
        "Profile deleted. Uploaded documents can be deleted in Data & privacy.",
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <>
      <PageTitle
        eyebrow="03 / BUILD YOUR SKILL PASSPORT"
        title="More than your resume."
        description="Your projects, experiences and self-assessed skills — in one editable, evidence-aware profile."
        action={
          <button
            className="button"
            onClick={() => {
              if (!confirmDiscard("profile")) return;
              w.selectProfile("");
              setDraft(blankProfile());
              setSaved(false);
              setDirty(false);
            }}
          >
            <Plus size={16} /> New profile
          </button>
        }
      />
      {error && <Notice tone="error">{error}</Notice>}
      <div className="profile-layout">
        <div>
          <section className="card">
            <div className="section-heading">
              <h2>The basics</h2>
              <span className="pill">
                {saved ? `Saved · v${draft.revision}` : "New draft"}
              </span>
            </div>
            <div className="import-bar">
              <div>
                <strong>Start from a reviewed resume</strong>
                <p>
                  {w.resume?.source_file ||
                    "Upload and review a resume in step 2"}
                </p>
              </div>
              <button
                className="button small"
                disabled={!w.resume}
                onClick={() => void importResume()}
              >
                <Download size={15} /> Import
              </button>
            </div>
            {w.resume && (
              <label className="check">
                <input
                  type="checkbox"
                  checked={replace}
                  onChange={(e) => setReplace(e.target.checked)}
                />{" "}
                Replace existing basic/section values; otherwise fill empty
                fields only
              </label>
            )}
            <div className="form-grid">
              <label>
                Full name
                <input
                  aria-label="Full name"
                  value={draft.name}
                  onChange={(e) => edit({ name: e.target.value })}
                  required
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={draft.email}
                  onChange={(e) => edit({ email: e.target.value })}
                />
              </label>
            </div>
            <p className="fine-print">
              CV reference:{" "}
              {draft.cv_file
                ? "Attached private resume document"
                : "Import a reviewed uploaded resume to attach your CV."}
            </p>
            <details>
              <summary>Attach or replace your CV directly</summary>
              <UploadBox
                allowHosted={false}
                endpoint="/documents"
                onResult={(document: { id: string }) => {
                  edit({ cv_file: document.id });
                  w.notify(
                    "CV attached to draft. Save the profile to persist this reference.",
                  );
                }}
              />
            </details>
          </section>
          <section className="card">
            <h2>Your experience</h2>
            <div className="form-grid">
              {(
                [
                  "education",
                  "projects",
                  "experience",
                  "internships",
                  "hackathons",
                  "certifications",
                  "preferred_roles",
                  "achievements",
                ] as const
              ).map((field) => (
                <label key={field} className="capitalize">
                  {field.replace("_", " ")}
                  <textarea
                    rows={3}
                    value={draft[field].join("\n")}
                    onChange={(e) =>
                      edit({
                        [field]: e.target.value.split("\n"),
                      })
                    }
                    placeholder="One entry per line"
                  />
                </label>
              ))}
            </div>
          </section>
          <section className="card">
            <div className="section-heading">
              <h2>Skills & evidence passport</h2>
              <span className="pill">{draft.skills.length} claims</span>
            </div>
            <SkillEditor
              skills={draft.skills}
              onChange={(skills) => edit({ skills })}
            />
          </section>
        </div>
        <aside>
          <section className="card ratings-card">
            <div className="eyebrow">12 RADIX CATEGORIES</div>
            <h2>Assess your starting point.</h2>
            <p className="muted">
              Self-reported competency, separate from extraction confidence.
              Leave unassessed categories unknown.
            </p>
            <details>
              <summary>How to use this scale</summary>
              <p className="fine-print">
                Team-designed anchors: 1–2 introductory; 3–4 guided practice;
                5–6 independent routine work; 7–8 complex work; 9–10 deep
                expertise. This rubric is not an official employer assessment.
              </p>
            </details>
            {draft.ratings.map((r) => (
              <label className="rating-field" key={r.category_code}>
                <span>
                  <b>{r.category_code}</b> {categories[r.category_code]}
                </span>
                <select
                  aria-label={`${r.category_code} competency`}
                  value={r.level ?? ""}
                  onChange={(e) =>
                    edit({
                      ratings: draft.ratings.map((x) =>
                        x.category_code === r.category_code
                          ? {
                              ...x,
                              level: e.target.value
                                ? Number(e.target.value)
                                : null,
                            }
                          : x,
                      ),
                    })
                  }
                >
                  <option value="">Unknown</option>
                  {Array.from({ length: 10 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1} / 10
                    </option>
                  ))}
                </select>
              </label>
            ))}
            <div className="completion-bar">
              <span
                style={{
                  width: `${(draft.ratings.filter((r) => r.level !== null).length / 12) * 100}%`,
                }}
              />
            </div>
            <p className="fine-print">
              {draft.ratings.filter((r) => r.level !== null).length}/12 assessed
              · all 12 required for a final readiness score
            </p>
          </section>
        </aside>
      </div>
      <div className="sticky-actions">
        <span>
          {dirty
            ? "Unsaved profile changes"
            : saved
              ? `Editing saved profile · revision ${draft.revision}`
              : "Draft profile · save to evaluate"}
        </span>
        <div>
          {saved && (
            <button className="button danger" onClick={() => void remove()}>
              <Trash2 size={15} /> Delete profile
            </button>
          )}
          <button
            className="button primary"
            disabled={busy || !draft.name.trim()}
            onClick={() => void save()}
          >
            <Save size={16} />
            {busy ? "Saving…" : "Save profile"}
          </button>
        </div>
      </div>
      {saved && (
        <div className="next-step">
          <p>
            Your saved profile can now be compared with a job. Company readiness
            is a separate optional comparison.
          </p>
          <div className="next-actions">
            <NextButton onClick={() => w.navigate(w.jd ? "matching" : "jd")}>
              {w.jd ? "See your JD match" : "Add a job description"}
            </NextButton>
            <button className="button" onClick={() => w.navigate("talent")}>
              Run Talent Check
            </button>
          </div>
        </div>
      )}
    </>
  );
}
