import { ArrowRight, Check, FileSearch, UserRound } from "lucide-react";
import { useWorkspace } from "../../shared/ui/context";

export default function MatchLauncher() {
  const w = useWorkspace();
  return (
    <section className="card match-launcher" aria-label="CV to job comparison">
      <div className="section-heading">
        <div>
          <div className="eyebrow">START HERE / CV → JOB → RESULTS</div>
          <h2>See how your CV matches a job.</h2>
          <p>
            Choose your saved candidate and job above. Company benchmarks and
            twelve self-ratings are optional for this comparison.
          </p>
        </div>
      </div>
      <div className="launcher-inputs">
        <button onClick={() => w.navigate(w.profile ? "profile" : "resume")}>
          <UserRound size={20} />
          <span>
            <small>1. YOUR CV / PROFILE</small>
            <strong>{w.profile?.name || "Upload your CV"}</strong>
            <span>
              {w.profile
                ? `${w.profile.skills.length} saved skill claims`
                : "PDF or DOCX → review extracted skills"}
            </span>
          </span>
          {w.profile && <Check size={17} />}
        </button>
        <button onClick={() => w.navigate("jd")}>
          <FileSearch size={20} />
          <span>
            <small>2. TARGET JOB</small>
            <strong>
              {w.jd
                ? `${w.jd.company || "Job"} · ${w.jd.role || w.jd.source_file}`
                : "Paste or upload the JD"}
            </strong>
            <span>
              {w.jd
                ? `${w.jd.skills.length} extracted requirements`
                : "Paste the complete job description"}
            </span>
          </span>
          {w.jd && <Check size={17} />}
        </button>
      </div>
      <div className="card-footer">
        <span className="muted">
          3. Get matched claims, evidence gaps and Career GPS.
        </span>
        <button
          className="button primary"
          onClick={() =>
            w.navigate(!w.profile ? "resume" : !w.jd ? "jd" : "matching")
          }
        >
          {w.profile && w.jd
            ? "Open JD match"
            : !w.profile
              ? "Upload my CV"
              : "Add the job description"}
          <ArrowRight size={16} />
        </button>
      </div>
    </section>
  );
}
