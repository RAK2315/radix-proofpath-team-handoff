import React, { useCallback, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import SelectedPage from "@selected-module";
import SelectedEvidence from "@selected-evidence";
import { api } from "../../shared/ui/api";
import { WorkspaceContext, type View } from "../../shared/ui/context";
import { Drawer, Notice } from "../../shared/ui/components";
import type {
  Company,
  Extraction,
  Profile,
} from "../../shared/contracts/types";
import "../web/styles.css";
import "./module.css";

const moduleName = import.meta.env.VITE_HANDOFF_MODULE || "jd_analytics";
const titles: Record<string, string> = {
  jd_analytics: "JD Analytics",
  resume_parsing: "Resume Parsing",
  profile_builder: "Profile Builder",
  talent_check: "Talent Check",
  skill_matching: "Skill Matching + Career GPS",
};
function stable<T extends { id: string; revision: number }>(
  old: T[],
  next: T[],
) {
  return next.map(
    (item) =>
      old.find((p) => p.id === item.id && p.revision === item.revision) || item,
  );
}
function ModuleWorkspace() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [jds, setJds] = useState<Extraction[]>([]);
  const [resumes, setResumes] = useState<Extraction[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [profileId, selectProfile] = useState("");
  const [jdId, selectJD] = useState("");
  const [resumeId, selectResume] = useState("");
  const [companyId, selectCompany] = useState("lab-data");
  const [status, setStatus] = useState<any>(null);
  const [message, notify] = useState("");
  const [drawer, setDrawer] = useState<any>(null);
  const requestVersion = useRef(0);
  const accept = useCallback((data: any) => {
    setProfiles((old) => stable(old, data.profiles));
    setJds((old) => stable(old, data.jds));
    setResumes((old) => stable(old, data.resumes));
    setCompanies(data.companies);
    selectProfile((id) => id || data.profiles[0]?.id || "");
    selectJD((id) => id || data.jds[0]?.id || "");
    selectResume((id) => id || data.resumes[0]?.id || "");
  }, []);
  const refresh = useCallback(async () => {
    const revision = ++requestVersion.current;
    const data = await api("/handoff/context");
    if (revision === requestVersion.current) accept(data);
  }, [accept]);
  useEffect(() => {
    void api("/status")
      .then(setStatus)
      .catch((e) => notify(e.message));
    void refresh().catch((e) => notify(e.message));
  }, [refresh]);
  const cacheExtraction = (value: Extraction) => {
    requestVersion.current++;
    const update = (rows: Extraction[]) => [
      value,
      ...rows.filter((row) => row.id !== value.id),
    ];
    if (value.source_type === "jd") setJds(update);
    else setResumes(update);
  };
  const cacheProfile = (value: Profile) => {
    requestVersion.current++;
    setProfiles((rows) => [
      value,
      ...rows.filter((row) => row.id !== value.id),
    ]);
  };
  const navigate = (_view: View) =>
    notify(
      "This workspace runs only your module. Use the root integrated app for the full journey.",
    );
  return (
    <WorkspaceContext.Provider
      value={{
        profiles,
        jds,
        resumes,
        companies,
        profile: profiles.find((p) => p.id === profileId) || null,
        jd: jds.find((p) => p.id === jdId) || null,
        resume: resumes.find((p) => p.id === resumeId) || null,
        company: companies.find((p) => p.id === companyId) || null,
        mode: "synthetic",
        status,
        refresh,
        refreshCompanies: refresh,
        cacheExtraction,
        cacheProfile,
        selectProfile,
        selectJD,
        selectResume,
        selectCompany,
        setMode: () =>
          notify(
            "This isolated teaching workspace uses labelled synthetic benchmarks. Configure real data only in the authorized integrated app.",
          ),
        navigate,
        notify,
        showEvidence: setDrawer,
        showReceipt: async (id) => {
          try {
            setDrawer(await api(`/receipts/${id}`));
          } catch (e) {
            notify((e as Error).message);
          }
        },
      }}
    >
      <main className="module-shell">
        <header className="module-header">
          <div>
            <div className="eyebrow">RADIX / INDEPENDENT MODULE WORKSPACE</div>
            <h1>{titles[moduleName]}</h1>
          </div>
          <button
            className="button"
            onClick={async () => {
              try {
                accept(await api("/handoff/seed", { method: "POST" }));
                notify(
                  "Pre-reviewed synthetic fixtures loaded; upload fresh input to test parsing.",
                );
              } catch (e) {
                notify((e as Error).message);
              }
            }}
          >
            Load synthetic inputs
          </button>
        </header>
        <Notice>
          SYNTHETIC TEACHING WORKSPACE - no official company benchmarks. Loaded
          fixtures are not fresh LLM extraction.
        </Notice>
        <section className="card module-selectors">
          <label>
            Candidate profile
            <select
              aria-label="Candidate profile"
              value={profileId}
              onChange={(e) => selectProfile(e.target.value)}
            >
              <option value="">Choose a profile</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Job description
            <select
              aria-label="Job description"
              value={jdId}
              onChange={(e) => selectJD(e.target.value)}
            >
              <option value="">Choose a JD</option>
              {jds.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.role || p.source_file}
                </option>
              ))}
            </select>
          </label>
          <label>
            Reviewed resume
            <select
              aria-label="Reviewed resume"
              value={resumeId}
              onChange={(e) => selectResume(e.target.value)}
            >
              <option value="">Choose a resume</option>
              {resumes.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name || p.source_file}
                </option>
              ))}
            </select>
          </label>
          <label>
            Synthetic company
            <select
              aria-label="Synthetic company"
              value={companyId}
              onChange={(e) => selectCompany(e.target.value)}
            >
              {companies.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        </section>
        {message && <Notice>{message}</Notice>}
        <SelectedPage />
        {drawer && (
          <Drawer value={drawer} onClose={() => setDrawer(null)}>
            <SelectedEvidence
              decision={drawer}
              onExplore={() => {
                setDrawer(null);
                requestAnimationFrame(() =>
                  document.getElementById("career-gps")?.scrollIntoView(),
                );
              }}
            />
          </Drawer>
        )}
      </main>
    </WorkspaceContext.Provider>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ModuleWorkspace />
  </React.StrictMode>,
);
