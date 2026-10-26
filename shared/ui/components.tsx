import { useState } from "react";
import {
  ArrowRight,
  Check,
  ChevronRight,
  FileText,
  Plus,
  Trash2,
  UploadCloud,
} from "lucide-react";
import { categories, manualSkill } from "../contracts/types";
import skillFamilies from "../contracts/skill-families.json";
import type { Skill } from "../contracts/types";
import { api } from "./api";
import { useWorkspace } from "./context";

export function PageTitle({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="page-title">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}
export function Notice({
  children,
  tone = "info",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`notice ${tone}`}
    >
      {children}
    </div>
  );
}
export function Empty({
  title,
  description,
  onClick,
  label,
}: {
  title: string;
  description: string;
  onClick?: () => void;
  label?: string;
}) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <FileText size={28} />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {onClick && (
        <button className="button primary" onClick={onClick}>
          {label}
          <ArrowRight size={16} />
        </button>
      )}
    </div>
  );
}
export function UploadBox({
  endpoint,
  onResult,
  allowHosted = true,
}: {
  endpoint: string;
  onResult: (value: any) => void | Promise<void>;
  allowHosted?: boolean;
}) {
  const { status } = useWorkspace();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [hosted, setHosted] = useState(false);
  async function upload(file?: File) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const data = new FormData();
      data.append("file", file);
      data.append("hosted_consent", String(hosted));
      await onResult(await api(endpoint, { method: "POST", body: data }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <label
        className={`upload-box ${busy ? "busy" : ""}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!busy) void upload(e.dataTransfer.files[0]);
        }}
      >
        <UploadCloud size={30} />
        <strong>
          {busy ? "Reading and extracting…" : "Drop your document here"}
        </strong>
        <span>
          or <u>browse files</u> · PDF or DOCX · up to 10 MB
        </span>
        <input
          aria-label="Upload document"
          type="file"
          accept=".pdf,.docx"
          disabled={busy}
          onChange={(e) => {
            void upload(e.target.files?.[0]);
            e.target.value = "";
          }}
        />
      </label>
      <div className="upload-footer">
        <span>
          <span className="status-dot" />{" "}
          {hosted
            ? "Hosted AI processing selected"
            : "Rules processing on backend · human review required"}
        </span>
        {allowHosted && status?.llm_configured && (
          <label className="check">
            <input
              type="checkbox"
              checked={hosted}
              onChange={(e) => setHosted(e.target.checked)}
            />{" "}
            Allow {status?.llm_provider || "Groq"} to process this document text
          </label>
        )}
      </div>
      {error && <Notice tone="error">{error}</Notice>}
    </>
  );
}
export function SkillEditor({
  skills,
  onChange,
  readOnly = false,
}: {
  skills: Skill[];
  onChange?: (skills: Skill[]) => void;
  readOnly?: boolean;
}) {
  const { showEvidence } = useWorkspace();
  const [search, setSearch] = useState("");
  const [family, setFamily] = useState("");
  const [expanded, setExpanded] = useState(false);
  const filtered = skills.filter(
    (s) =>
      (!family || s.skill_family === family) &&
      `${s.skill_name} ${s.skill_family} ${categories[s.category_code] || "Other"}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  );
  const families = [
    ...new Set(skills.map((s) => s.skill_family || "Other")),
  ].sort();
  const edit = (id: string, patch: Partial<Skill>) =>
    onChange?.(skills.map((s) => (s.skill_id === id ? { ...s, ...patch } : s)));
  return (
    <>
      <div className="section-bar skill-toolbar">
        <input
          className="search-input"
          aria-label="Search skills"
          placeholder="Filter skills…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          aria-label="Filter skill family"
          value={family}
          onChange={(e) => {
            setFamily(e.target.value);
            setExpanded(false);
          }}
        >
          <option value="">All skill families ({skills.length})</option>
          {families.map((name) => (
            <option key={name} value={name}>
              {name} (
              {
                skills.filter((s) => (s.skill_family || "Other") === name)
                  .length
              }
              )
            </option>
          ))}
        </select>
        {!readOnly && (
          <button
            className="button small"
            onClick={() => {
              setFamily("");
              setSearch("New skill");
              onChange?.([...skills, manualSkill()]);
            }}
          >
            <Plus size={15} /> Add skill
          </button>
        )}
      </div>
      <p className="fine-print">
        Browse descriptive skill families. RADIX category codes remain the
        separate twelve-category competency framework.
      </p>
      <div className="skill-list">
        {(expanded ? filtered : filtered.slice(0, 8)).map((s) => (
          <div className="skill-row" key={s.skill_id}>
            <span className="category-chip">{s.category_code}</span>
            <div className="skill-main">
              {readOnly ? (
                <strong>{s.skill_name}</strong>
              ) : (
                <input
                  aria-label="Skill name"
                  value={s.skill_name}
                  onChange={(e) =>
                    edit(s.skill_id, {
                      skill_name: e.target.value,
                      source_type: "manual",
                      source_file: null,
                      source_page: null,
                      source_start: null,
                      source_end: null,
                      normalized_name: null,
                      claim_basis: "explicit",
                      source_document_id: null,
                      evidence: "User-corrected skill claim",
                      confidence: "low",
                      evidence_type: "manual_entry",
                      claim_status: "claimed",
                    })
                  }
                />
              )}
              {readOnly ? (
                <small className="skill-family">
                  {s.skill_family || "Other"}
                </small>
              ) : (
                <select
                  className="skill-family-select"
                  aria-label={`Skill family for ${s.skill_name}`}
                  value={s.skill_family || "Other"}
                  onChange={(e) =>
                    edit(s.skill_id, { skill_family: e.target.value })
                  }
                >
                  {skillFamilies.map((name) => (
                    <option key={name}>{name}</option>
                  ))}
                </select>
              )}
              <button className="evidence-link" onClick={() => showEvidence(s)}>
                <FileText size={12} />{" "}
                {s.source_type === "manual"
                  ? "Self-reported claim"
                  : "View source evidence"}
                <ChevronRight size={12} />
              </button>
              {s.claim_status === "needs_review" && (
                <label className="check claim-review">
                  <input
                    type="checkbox"
                    checked={false}
                    onChange={() =>
                      edit(s.skill_id, { claim_status: "claimed" })
                    }
                  />{" "}
                  Unreviewed claim — confirm after checking the source
                </label>
              )}
            </div>
            {!readOnly && (
              <select
                aria-label={`Category for ${s.skill_name}`}
                value={s.category_code}
                onChange={(e) =>
                  edit(s.skill_id, {
                    category_code: e.target.value as Skill["category_code"],
                  })
                }
              >
                {[...Object.entries(categories), ["OTHER", "Other"]].map(
                  ([code, name]) => (
                    <option key={code} value={code}>
                      {code} · {name}
                    </option>
                  ),
                )}
              </select>
            )}
            <span className={`confidence ${s.confidence}`}>
              {s.confidence} confidence
            </span>
            {!readOnly && (
              <button
                className="icon-button"
                aria-label={`Remove ${s.skill_name}`}
                onClick={() =>
                  onChange?.(skills.filter((x) => x.skill_id !== s.skill_id))
                }
              >
                <Trash2 size={15} />
              </button>
            )}
          </div>
        ))}
      </div>
      {filtered.length > 8 && (
        <button
          className="button small skill-expand"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded
            ? "Show fewer skills"
            : `Show all ${filtered.length} skills`}
        </button>
      )}
      {skills.length > 0 && filtered.length === 0 && (
        <p className="muted">
          No skills match this filter. Choose another family or clear your
          search.
        </p>
      )}
      {skills.length === 0 && (
        <p className="muted">
          No skill claims yet. Add a skill or review an uploaded document.
        </p>
      )}
    </>
  );
}
export { default as Drawer } from "./EvidenceDrawer";
export function Score({
  value,
  label,
  small = false,
}: {
  value: number | null | undefined;
  label: string;
  small?: boolean;
}) {
  return (
    <div className={`score ${small ? "small" : ""}`}>
      <span>
        {value == null ? "—" : value.toFixed(1)}
        <small>{value != null ? "%" : ""}</small>
      </span>
      <p>{label}</p>
    </div>
  );
}
export function NextButton({
  children,
  onClick,
}: {
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button className="button primary" onClick={onClick}>
      {children}
      <ArrowRight size={16} />
    </button>
  );
}
export function SavedBadge() {
  return (
    <span className="saved-badge">
      <Check size={13} /> Saved & reviewed
    </span>
  );
}
