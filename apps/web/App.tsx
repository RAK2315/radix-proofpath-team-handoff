import { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BriefcaseBusiness,
  Check,
  ChevronRight,
  Compass,
  FileSearch,
  FileText,
  Fingerprint,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  Target,
  Trash2,
  UserRound,
  X,
} from "lucide-react";
import JDAnalyticsPage from "../../jd_analytics/frontend/JDAnalyticsPage";
import ResumeParsingPage from "../../resume_parsing/frontend/ResumeParsingPage";
import ProfileBuilderPage from "../../profile_builder/frontend/ProfileBuilderPage";
import TalentCheckPage from "../../talent_check/frontend/TalentCheckPage";
import SkillMatchingPage from "../../skill_matching/frontend/SkillMatchingPage";
import MatchLauncher from "../../skill_matching/frontend/MatchLauncher";
import ReasoningChain from "../../skill_matching/frontend/ReasoningChain";
import { loadSyntheticWalkthrough } from "../../shared/ui/synthetic";
import type {
  BenchmarkMode,
  Company,
  Extraction,
  Profile,
} from "../../shared/contracts/types";
import { api } from "../../shared/ui/api";
import { WorkspaceContext } from "../../shared/ui/context";
import type { View } from "../../shared/ui/context";
import { Drawer, Notice } from "../../shared/ui/components";
import { confirmDiscard } from "../../shared/ui/drafts";
import { useAuth } from "../../shared/ui/AuthGate";

const modules = [
  {
    id: "jd",
    name: "JD Analytics",
    subtitle: "Paste a JD · review requirements",
    navHint: "Requirements & sources",
    icon: FileSearch,
  },
  {
    id: "resume",
    name: "Resume Parsing",
    subtitle: "Upload CV · extract evidence",
    navHint: "Review CV evidence",
    icon: FileText,
  },
  {
    id: "profile",
    name: "Profile Builder",
    subtitle: "Edit and save your candidate",
    navHint: "Edit and save profile",
    icon: UserRound,
  },
  {
    id: "talent",
    name: "Talent Check",
    subtitle: "12 ratings + company benchmarks",
    navHint: "Company benchmarks",
    icon: Target,
  },
  {
    id: "matching",
    name: "Skill Matching",
    subtitle: "CV → JD fit + Career GPS",
    navHint: "JD fit + Career GPS",
    icon: Compass,
  },
] as const;

export default function App() {
  const auth = useAuth();
  const [view, setView] = useState<View>(
    (location.hash.slice(1) || "overview") as View,
  );
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [jds, setJds] = useState<Extraction[]>([]);
  const [resumes, setResumes] = useState<Extraction[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [profileId, selectProfile] = useState(
    sessionStorage.getItem("profile-id") || "",
  );
  const [jdId, selectJD] = useState(sessionStorage.getItem("jd-id") || "");
  const [resumeId, selectResume] = useState(
    sessionStorage.getItem("resume-id") || "",
  );
  const [companyId, selectCompany] = useState(
    sessionStorage.getItem("company-id") || "",
  );
  const [mode, setMode] = useState<BenchmarkMode>(
    sessionStorage.getItem("benchmark-mode") === "synthetic"
      ? "synthetic"
      : "real",
  );
  const [status, setStatus] = useState<any>(null);
  const [error, setError] = useState("");
  const [benchmarkError, setBenchmarkError] = useState("");
  const [toast, notify] = useState("");
  const [drawer, setDrawer] = useState<any>(null);
  const [mobile, setMobile] = useState(false);
  const [privacy, setPrivacy] = useState(false);
  const [docs, setDocs] = useState<any[]>([]);
  const [labBusy, setLabBusy] = useState(false);
  const workspaceRequest = useRef(0);
  const profile = profiles.find((p) => p.id === profileId) || null,
    jd = jds.find((p) => p.id === jdId) || null,
    resume = resumes.find((p) => p.id === resumeId) || null,
    company = companies.find((c) => c.id === companyId) || null;
  const refresh = useCallback(async () => {
    const requestVersion = ++workspaceRequest.current;
    const [p, j, r] = await Promise.all([
      api<Profile[]>("/profiles"),
      api<Extraction[]>("/jd"),
      api<Extraction[]>("/resumes"),
    ]);
    // A response started before an upload/save must not erase its accepted cache.
    if (requestVersion !== workspaceRequest.current) return;
    setProfiles((old) =>
      p.map(
        (item) =>
          old.find((x) => x.id === item.id && x.revision === item.revision) ||
          item,
      ),
    );
    setJds((old) =>
      j.map(
        (item) =>
          old.find((x) => x.id === item.id && x.revision === item.revision) ||
          item,
      ),
    );
    setResumes((old) =>
      r.map(
        (item) =>
          old.find((x) => x.id === item.id && x.revision === item.revision) ||
          item,
      ),
    );
  }, []);
  function cacheExtraction(value: Extraction) {
    workspaceRequest.current++;
    const update = (rows: Extraction[]) => [
      value,
      ...rows.filter((row) => row.id !== value.id),
    ];
    if (value.source_type === "jd") setJds(update);
    else setResumes(update);
  }
  function cacheProfile(value: Profile) {
    workspaceRequest.current++;
    setProfiles((rows) => [
      value,
      ...rows.filter((row) => row.id !== value.id),
    ]);
  }
  async function refreshCompanies() {
    const data = await api(`/talent-check/companies?mode=${mode}&refresh=true`);
    setCompanies(data.companies);
    setError("");
  }
  useEffect(() => {
    void api("/status")
      .then(setStatus)
      .catch((e) => setError(e.message));
    void refresh().catch((e) => setError(e.message));
  }, [refresh]);
  useEffect(() => {
    let cancelled = false;
    void api(`/talent-check/companies?mode=${mode}`)
      .then((data) => {
        if (!cancelled) {
          setCompanies(data.companies);
          setBenchmarkError("");
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setCompanies([]);
          setBenchmarkError(e.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [mode]);
  useEffect(() => {
    for (const [key, value] of Object.entries({
      "profile-id": profileId,
      "jd-id": jdId,
      "resume-id": resumeId,
      "company-id": companyId,
      "benchmark-mode": mode,
    }))
      sessionStorage.setItem(key, value);
  }, [profileId, jdId, resumeId, companyId, mode]);
  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => notify(""), 5000);
    return () => clearTimeout(id);
  }, [toast]);
  useEffect(() => {
    const fn = () => setView((location.hash.slice(1) || "overview") as View);
    window.addEventListener("hashchange", fn);
    return () => window.removeEventListener("hashchange", fn);
  }, []);
  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setDrawer(null);
        setPrivacy(false);
        setMobile(false);
      }
    };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, []);
  const navigate = (next: View) => {
    location.hash = next;
    setView(next);
    setMobile(false);
  };
  async function showReceipt(id: string) {
    try {
      setDrawer(await api(`/receipts/${id}`));
    } catch (e) {
      notify((e as Error).message);
    }
  }
  async function openPrivacy() {
    setPrivacy(true);
    try {
      setDocs(await api("/documents"));
    } catch (e) {
      notify((e as Error).message);
    }
  }
  async function loadLab() {
    setLabBusy(true);
    try {
      const { jd: j, resume: r, profile: p } = await loadSyntheticWalkthrough();
      await refresh();
      selectJD(j.id);
      selectResume(r.id);
      selectProfile(p.id);
      setMode("synthetic");
      selectCompany("lab-systems");
      notify(
        "Synthetic walkthrough loaded. All examples and self-ratings are invented lab fixtures.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLabBusy(false);
    }
  }
  const completed = [
    Boolean(jd?.review_status === "reviewed"),
    Boolean(resume?.review_status === "reviewed"),
    Boolean(profile),
    Boolean(
      profile && company && profile.ratings.every((r) => r.level !== null),
    ),
    Boolean(profile && jd),
  ];
  return (
    <WorkspaceContext.Provider
      value={{
        profiles,
        jds,
        resumes,
        profile,
        jd,
        resume,
        company,
        companies,
        mode,
        status,
        refresh,
        refreshCompanies,
        cacheExtraction,
        cacheProfile,
        selectProfile,
        selectJD,
        selectResume,
        selectCompany,
        setMode,
        navigate,
        notify,
        showEvidence: setDrawer,
        showReceipt,
      }}
    >
      <div className="app-layout">
        <aside className={`sidebar ${mobile ? "open" : ""}`}>
          <a className="brand" href="#overview">
            <span className="brand-mark">
              <Fingerprint size={28} />
            </span>
            <div>
              RADIX<span>PROOFPATH</span>
            </div>
          </a>
          <div className="sidebar-label">YOUR WORKSPACE</div>
          <button
            className={`nav-item ${view === "overview" ? "active" : ""}`}
            onClick={() => navigate("overview")}
          >
            <LayoutDashboard size={18} />
            <span>Overview</span>
          </button>
          <div className="sidebar-label journey-label">
            Candidate journey <span>05</span>
          </div>
          <nav>
            {modules.map((m, i) => (
              <button
                key={m.id}
                className={`nav-item ${view === m.id ? "active" : ""}`}
                onClick={() => navigate(m.id)}
              >
                <m.icon size={18} />
                <span>
                  {m.name}
                  <em className="nav-description">{m.navHint}</em>
                </span>
                <small>{String(i + 1).padStart(2, "0")}</small>
              </button>
            ))}
          </nav>
          <button className="privacy-button" onClick={() => void openPrivacy()}>
            <LockKeyhole size={15} /> Data & privacy <ArrowUpRight size={14} />
          </button>
          {auth.signOut && (
            <button
              className="privacy-button"
              onClick={() => {
                if (confirmDiscard()) void auth.signOut?.();
              }}
            >
              Sign out · {auth.email}
            </button>
          )}
          <div className="sidebar-profile">
            <span className="avatar">{profile?.name?.slice(0, 1) || "P"}</span>
            <div>
              <strong>{profile?.name || "Your workspace"}</strong>
              <small>
                {status?.auth_mode === "local"
                  ? "Local · single user"
                  : "Authenticated workspace"}
              </small>
            </div>
          </div>
        </aside>
        <div className="main-shell">
          <header className="topbar">
            <button
              className="icon-button mobile-toggle"
              aria-label="Toggle navigation"
              onClick={() => setMobile(!mobile)}
            >
              <Menu />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span> <ChevronRight size={16} />
              <strong>
                {view === "overview"
                  ? "Overview"
                  : modules.find((m) => m.id === view)?.name}
              </strong>
            </div>
            <div className="topbar-right">
              <span className="connection">
                <span className="status-dot" />
                {status
                  ? `${status.storage_mode === "local" ? "Local persistence" : "Supabase persistence"}`
                  : "Connecting…"}
              </span>
              <span className="topbar-separator" />
              <span className="framework-badge">12-SKILL FRAMEWORK</span>
            </div>
          </header>
          <main>
            <div className="workspace-context">
              <label>
                <UserRound size={14} />
                <span className="context-label">Candidate profile</span>
                <select
                  aria-label="Selected candidate"
                  value={profileId}
                  onChange={(e) => {
                    if (confirmDiscard("profile"))
                      selectProfile(e.target.value);
                  }}
                >
                  <option value="">Choose candidate</option>
                  {profiles.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <BriefcaseBusiness size={14} />
                <span className="context-label">Job description</span>
                <select
                  aria-label="Selected job"
                  value={jdId}
                  onChange={(e) => {
                    if (confirmDiscard("jd")) selectJD(e.target.value);
                  }}
                >
                  <option value="">Choose a job</option>
                  {jds.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.company ? `${j.company} · ` : ""}
                      {j.role || j.source_file}
                    </option>
                  ))}
                </select>
              </label>
              <details className="benchmark-selectors" open={view === "talent"}>
                <summary>
                  Company readiness settings{" "}
                  <small>Optional for JD matching</small>
                </summary>
                <label>
                  <Target size={14} />
                  <select
                    aria-label="Selected company"
                    value={companyId}
                    onChange={(e) => selectCompany(e.target.value)}
                  >
                    <option value="">Choose company</option>
                    {companies.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </label>
                <select
                  aria-label="Benchmark data mode"
                  className={`data-mode ${mode}`}
                  value={mode}
                  onChange={(e) => setMode(e.target.value as BenchmarkMode)}
                >
                  <option value="real">Real company data</option>
                  <option value="synthetic">Synthetic lab</option>
                </select>
              </details>
            </div>
            {error && (
              <Notice tone={mode === "real" ? "info" : "error"}>{error}</Notice>
            )}
            {view === "talent" && benchmarkError && (
              <Notice>{benchmarkError}</Notice>
            )}
            {mode === "synthetic" && (
              <div className="lab-ribbon">
                SYNTHETIC LAB{" "}
                <span>
                  Invented companies, benchmarks and example documents for
                  testing. Real-data verification is separate.
                </span>
              </div>
            )}
            <div hidden={view !== "overview"}>
              <header className="overview-header">
                <div>
                  <div className="eyebrow">YOUR CAREER WORKSPACE</div>
                  <h1>Your potential. Backed by proof.</h1>
                  <p>
                    Understand the job, review your evidence and choose your
                    next step.
                  </p>
                </div>
                <div className="overview-actions">
                  <button className="button" onClick={() => navigate("jd")}>
                    Add a job description <ArrowUpRight size={17} />
                  </button>
                  <button
                    className="text-button"
                    disabled={labBusy}
                    onClick={() => void loadLab()}
                  >
                    {labBusy
                      ? "Loading lab documents…"
                      : "Explore a synthetic walkthrough"}{" "}
                    <ArrowRight size={15} />
                  </button>
                </div>
              </header>
              <MatchLauncher />
              <section className="journey-section">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">FIVE CONNECTED MODULES</div>
                    <h2>Your workspace, step by step.</h2>
                  </div>
                  <span className="journey-count">
                    {completed.filter(Boolean).length}
                    <small> / 5 inputs ready</small>
                  </span>
                </div>
                <div className="journey-cards">
                  {modules.map((m, i) => (
                    <button
                      className={`journey-card ${completed[i] ? "ready" : ""}`}
                      key={m.id}
                      onClick={() => navigate(m.id)}
                    >
                      <span className="journey-card-top">
                        <m.icon size={22} />
                        <span>{String(i + 1).padStart(2, "0")}</span>
                      </span>
                      <h3>{m.name}</h3>
                      <p>{m.subtitle}</p>
                      <div>
                        {completed[i] ? (
                          <>
                            <Check size={13} /> Inputs ready
                          </>
                        ) : (
                          <>
                            Explore module <ArrowRight size={13} />
                          </>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </section>
              <div className="overview-bottom">
                <section className="card candidate-card">
                  <div className="section-heading">
                    <h3>Your skill passport</h3>
                    <button
                      className="text-button"
                      onClick={() => navigate("profile")}
                    >
                      {profile ? "View profile" : "Create profile"}
                      <ArrowUpRight size={15} />
                    </button>
                  </div>
                  <div className="candidate-info">
                    <span className="large-avatar">
                      {profile?.name?.slice(0, 1) || <UserRound size={30} />}
                    </span>
                    <div>
                      <h2>{profile?.name || "Your story goes here."}</h2>
                      <p>
                        {profile
                          ? `${profile.skills.length} skill claims · ${profile.ratings.filter((r) => r.level !== null).length}/12 categories assessed`
                          : "Bring your skills, projects and experience together."}
                      </p>
                    </div>
                  </div>
                  <div className="passport-footer">
                    <Fingerprint size={17} />
                    <span>
                      Every claim has a source. Every gap has a next step.
                    </span>
                  </div>
                </section>
                <section className="principle-card">
                  <div className="eyebrow">TWO DISTINCT COMPARISONS</div>
                  <h3>Job fit or company readiness?</h3>
                  <p>
                    Job fit compares your claims with one JD. Company readiness
                    compares twelve self-ratings with a company's benchmark.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => navigate("talent")}
                  >
                    Understand your readiness <ArrowRight size={15} />
                  </button>
                </section>
              </div>
              <footer className="page-footer">
                <span>RADIX ProofPath · Built for the candidate.</span>
                <span>
                  Transparent logic. Traceable evidence. Your next move.
                </span>
              </footer>
            </div>
            <div hidden={view !== "jd"}>
              <JDAnalyticsPage />
            </div>
            <div hidden={view !== "resume"}>
              <ResumeParsingPage />
            </div>
            <div hidden={view !== "profile"}>
              <ProfileBuilderPage />
            </div>
            <div hidden={view !== "talent"}>
              <TalentCheckPage />
            </div>
            <div hidden={view !== "matching"}>
              <SkillMatchingPage />
            </div>
          </main>
        </div>
      </div>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          {toast}
        </div>
      )}
      {drawer && (
        <Drawer value={drawer} onClose={() => setDrawer(null)}>
          {drawer.jd_evidence && (
            <ReasoningChain
              decision={drawer}
              onExplore={() => {
                setDrawer(null);
                navigate("matching");
                requestAnimationFrame(() =>
                  document
                    .getElementById("career-gps")
                    ?.scrollIntoView({ behavior: "smooth", block: "start" }),
                );
              }}
            />
          )}
        </Drawer>
      )}
      {privacy && (
        <div className="drawer-backdrop" onClick={() => setPrivacy(false)}>
          <aside
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Data and privacy"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="section-bar">
              <h2>Data & privacy</h2>
              <button
                className="icon-button"
                aria-label="Close privacy"
                onClick={() => setPrivacy(false)}
              >
                <X />
              </button>
            </div>
            <p>
              Profiles persist until deleted. Uploaded originals/text expire
              after seven days when document cleanup runs on upload or document
              listing/access, or the separately configured maintenance job.
              Local development uses private SQLite; cloud mode uses Supabase.
              Hosted AI receives document text only when selected per input.
            </p>
            <Notice>
              Deleting a source removes its extraction and associated document
              claims; saved self-ratings remain self-reported. Derived
              evaluation receipts are invalidated.
            </Notice>
            {docs.map((d) => (
              <div className="privacy-document" key={d.id}>
                <FileText size={17} />
                <div>
                  <strong>{d.source_file}</strong>
                  <small>{new Date(d.created_at).toLocaleString()}</small>
                </div>
                <button
                  className="icon-button"
                  aria-label={`Delete ${d.source_file}`}
                  onClick={async () => {
                    try {
                      await api(`/documents/${d.id}`, { method: "DELETE" });
                      setDocs(docs.filter((x) => x.id !== d.id));
                      await refresh();
                      notify("Source document and dependent results removed.");
                    } catch (e) {
                      notify((e as Error).message);
                    }
                  }}
                >
                  <Trash2 size={17} />
                </button>
              </div>
            ))}
          </aside>
        </div>
      )}
    </WorkspaceContext.Provider>
  );
}
