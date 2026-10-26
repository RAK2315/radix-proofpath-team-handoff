import { useEffect, useRef, useState } from "react";
import {
  ArrowUpRight,
  Check,
  Compass,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";
import { categories } from "../../shared/contracts/types";
import { post } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import { Empty, Notice, PageTitle, Score } from "../../shared/ui/components";
export default function SkillMatchingPage() {
  const w = useWorkspace();
  const [result, setResult] = useState<any>(null);
  const [scenario, setScenario] = useState<any>(null);
  const [skills, setSkills] = useState<string[]>([]);
  const [levels, setLevels] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("missing");
  const [rank, setRank] = useState("match");
  const selectionKey = `${w.profile?.id}:${w.profile?.revision}:${w.jd?.id}:${w.jd?.revision}:${w.company?.id}:${w.mode}`;
  const activeKey = useRef(selectionKey);
  activeKey.current = selectionKey;
  const frozenHash = useRef<string | null>(null);
  useEffect(() => {
    setBusy(false);
    setError("");
    frozenHash.current = null;
    setResult(null);
    setScenario(null);
    setSkills([]);
    setLevels({});
  }, [
    w.profile?.id,
    w.profile?.revision,
    w.jd?.id,
    w.jd?.revision,
    w.company?.id,
    w.mode,
  ]);
  async function calculate() {
    if (!w.profile || !w.jd) return;
    setBusy(true);
    setError("");
    try {
      const match = await post("/matching/evaluate", {
        profile_id: w.profile.id,
        jd_id: w.jd.id,
      });
      if (activeKey.current !== selectionKey) return;
      frozenHash.current = null;
      setResult(match);
      setSkills([]);
      setLevels({});
    } catch (e) {
      if (activeKey.current === selectionKey) setError((e as Error).message);
    } finally {
      if (activeKey.current === selectionKey) setBusy(false);
    }
  }
  useEffect(() => {
    if (!result || !w.profile || !w.jd) return;
    let cancelled = false;
    setBusy(true);
    const timer = setTimeout(() => {
      post("/matching/scenarios/preview", {
        profile_id: w.profile!.id,
        profile_revision: w.profile!.revision,
        jd_id: w.jd!.id,
        jd_revision: w.jd!.revision,
        company_id: w.company?.id || null,
        benchmark_mode: w.mode,
        benchmark_hash: frozenHash.current,
        skill_overrides: skills,
        category_overrides: levels,
      })
        .then((value) => {
          if (!cancelled) {
            frozenHash.current =
              value.baseline_readiness?.benchmark_hash || null;
            setScenario(value);
          }
        })
        .catch((e) => {
          if (!cancelled) setError(e.message);
        })
        .finally(() => {
          if (!cancelled) setBusy(false);
        });
    }, 180);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // Frozen result revisions are checked by the server. Scenario response is deliberately not a dependency.
  }, [skills, levels, result, w.profile, w.jd, w.company, w.mode]);
  const decisions = result
    ? tab === "matched"
      ? result.matched_skills
      : tab === "ambiguous"
        ? result.ambiguous_matches
        : result.missing_skills
    : [];
  const recommendations = [...(scenario?.recommendations || [])].sort(
    (a, b) =>
      (b[rank === "match" ? "match_delta" : "readiness_delta"] || 0) -
      (a[rank === "match" ? "match_delta" : "readiness_delta"] || 0),
  );
  const missingNames = [
    ...new Set<string>(
      (result?.missing_skills || []).map((s: any) => s.skill_name),
    ),
  ];
  return (
    <>
      <PageTitle
        eyebrow="05 / MATCH THE ROLE. MAP THE NEXT MOVE."
        title="Find your path forward."
        description="CV → specific JD comparison. Select a candidate and job above, then analyze. Company benchmarks and numeric self-ratings are not required."
        action={
          <button
            className="button primary"
            disabled={!w.profile || !w.jd || busy}
            onClick={() => void calculate()}
          >
            <Sparkles size={16} />
            {busy ? "Calculating…" : "Analyze this match"}
          </button>
        }
      />
      {w.profile && w.jd && (
        <div className="pair-summary">
          <span>
            <strong>Candidate</strong> {w.profile.name}
          </span>
          <span>
            <strong>Target</strong> {w.jd.company || "Job"} ·{" "}
            {w.jd.role || w.jd.source_file}
          </span>
        </div>
      )}
      {error && <Notice tone="error">{error}</Notice>}
      {w.jd?.warnings.some((x) =>
        x.startsWith("Requirement not fully parsed;"),
      ) && (
        <Notice>
          Some requirement wording was not fully parsed. This percentage covers
          extracted groups only and stays provisional until you review the JD
          source and correct coverage.{" "}
          <button className="text-button" onClick={() => w.navigate("jd")}>
            Review JD coverage
          </button>
        </Notice>
      )}
      {!w.profile || !w.jd ? (
        <Empty
          title="Choose a candidate and a job."
          description="Save a profile and review a JD first. Matching evaluates that specific pair, not a generic company score."
          onClick={() => w.navigate(!w.jd ? "jd" : "profile")}
          label={!w.jd ? "Add a JD" : "Build a profile"}
        />
      ) : !result ? (
        <section className="card">
          <Empty
            title={`${w.profile.name} × ${w.jd.role || w.jd.source_file}`}
            description="Discover which requirements you cover, which are missing, and the evidence behind each decision."
            onClick={() => void calculate()}
            label="Generate my match report"
          />
        </section>
      ) : (
        <>
          <div className="match-summary card">
            <Score value={result.match_score} label="Specific-JD match" />
            <div className="match-summary-copy">
              <div className="eyebrow">
                {w.jd.company || "SELECTED JOB"} /{" "}
                {w.jd.role || w.jd.source_file}
              </div>
              <h2>Your match, explained.</h2>
              <p>
                {result.matched_skills.length} matched claims ·{" "}
                {result.missing_skills.length} evidence gaps ·{" "}
                {result.ambiguous_matches.length} need review
              </p>
              <button
                className="text-button"
                onClick={() => w.showReceipt(result.receipt_id)}
              >
                Follow the decision receipt <ArrowUpRight size={14} />
              </button>
            </div>
            <span className="pill">{result.status}</span>
          </div>
          <Notice>
            Score = coverage of extracted JD requirements by your reviewed CV
            claims. An evidence gap means the CV does not explicitly support the
            requirement; it does not prove you lack the skill. This is not a
            competency assessment or hiring probability. Unrecognized wording
            still needs human review.
          </Notice>
          <section className="card">
            <div className="section-heading">
              <h2>Requirement breakdown</h2>
              <div className="segmented">
                {[
                  ["missing", `Evidence gaps ${result.missing_skills.length}`],
                  ["matched", `Matched ${result.matched_skills.length}`],
                  ["ambiguous", `Review ${result.ambiguous_matches.length}`],
                ].map(([id, label]) => (
                  <button
                    key={id}
                    className={tab === id ? "selected" : ""}
                    onClick={() => setTab(id)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            {decisions.length === 0 ? (
              <p className="muted">No requirements in this view.</p>
            ) : (
              decisions.map((item: any, i: number) => (
                <button
                  className="decision-row"
                  key={`${item.requirement_id}-${i}`}
                  onClick={() => w.showEvidence(item)}
                >
                  <span
                    className={`decision-icon ${item.matched ? "yes" : "no"}`}
                  >
                    {item.matched ? <Check size={16} /> : <X size={16} />}
                  </span>
                  <div>
                    <strong>{item.skill_name}</strong>
                    <p>{item.reason}</p>
                  </div>
                  <span className="pill">{item.requirement_type}</span>
                  <ArrowUpRight size={15} />
                </button>
              ))
            )}
            <details className="methodology">
              <summary>Scoring rules & contributions</summary>
              <p>{result.methodology}</p>
              {result.contributions.map((g: any) => (
                <p key={g.requirement_id}>
                  {g.skills.join(` ${g.operator} `)} — coverage{" "}
                  {Math.round(g.coverage * 100)}% × weight {g.weight}
                  {g.score_contribution != null
                    ? ` · ${g.score_contribution.toFixed(2)} points out of 100`
                    : ""}
                </p>
              ))}
            </details>
          </section>
          <section
            className="gps"
            id="career-gps"
            aria-label="Career GPS hypothetical workspace"
          >
            <header className="gps-header">
              <div>
                <div className="eyebrow">
                  <Compass size={15} /> CAREER GPS / HYPOTHETICAL WORKSPACE
                </div>
                <h2>Your next move, made visible.</h2>
                <p>
                  Try a change. See its impact. Keep your real profile intact.
                </p>
              </div>
              <button
                className="button ghost"
                onClick={() => {
                  setSkills([]);
                  setLevels({});
                }}
              >
                <RotateCcw size={15} /> Reset scenario
              </button>
            </header>
            <div className="gps-scores">
              <div>
                <span>JD MATCH</span>
                <div className="before-after">
                  <b>{result.match_score ?? "—"}%</b>
                  <ArrowUpRight />
                  <b className="projected-score">
                    {scenario?.projected_match.match_score ?? "—"}%
                  </b>
                  <em>
                    {scenario?.match_delta != null
                      ? `${scenario.match_delta >= 0 ? "+" : ""}${scenario.match_delta} pts`
                      : "—"}
                  </em>
                </div>
              </div>
              <div>
                <span>
                  COMPANY READINESS{" "}
                  {w.mode === "synthetic" ? "· SYNTHETIC" : ""}
                </span>
                <div className="before-after">
                  <b>{scenario?.baseline_readiness?.readiness_score ?? "—"}%</b>
                  <ArrowUpRight />
                  <b>
                    {scenario?.projected_readiness?.readiness_score ?? "—"}%
                  </b>
                  <em>
                    {scenario?.readiness_delta != null
                      ? `${scenario.readiness_delta >= 0 ? "+" : ""}${scenario.readiness_delta} pts`
                      : "Needs benchmark + 12 ratings"}
                  </em>
                </div>
              </div>
            </div>
            <div className="gps-controls">
              <div>
                <h3>What if you covered these requirements?</h3>
                <p>
                  Named skill coverage changes JD fit; it does not imply a
                  category level.
                </p>
                <div className="scenario-skills">
                  {missingNames.map((name) => (
                    <label
                      className={skills.includes(name) ? "on" : ""}
                      key={name}
                    >
                      <input
                        type="checkbox"
                        checked={skills.includes(name)}
                        onChange={(e) =>
                          setSkills(
                            e.target.checked
                              ? [...skills, name]
                              : skills.filter((s) => s !== name),
                          )
                        }
                      />
                      {name}
                      <span>
                        {skills.includes(name)
                          ? "Added to scenario"
                          : "Hypothetical"}
                      </span>
                    </label>
                  ))}
                </div>
                {missingNames.length === 0 && (
                  <p>
                    All named requirements are already covered by your reviewed
                    claims.
                  </p>
                )}
              </div>
              <div>
                <h3>Explore category improvements</h3>
                <p>
                  Self-rating targets affect company readiness only. Unknown
                  baselines remain visible.
                </p>
                <div className="slider-grid">
                  {w.profile.ratings.map((r) => (
                    <label className="scenario-slider" key={r.category_code}>
                      <span title={r.category_code}>
                        <span>{categories[r.category_code]}</span>
                        <b>{levels[r.category_code] ?? r.level ?? "?"}</b>
                      </span>
                      <input
                        aria-label={`${r.category_code} hypothetical level`}
                        type="range"
                        min={1}
                        max={10}
                        step={1}
                        value={levels[r.category_code] ?? r.level ?? 1}
                        onChange={(e) =>
                          setLevels({
                            ...levels,
                            [r.category_code]: Number(e.target.value),
                          })
                        }
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <footer>
              <span className="status-dot" />
              {busy
                ? "Recalculating with the same scoring engines…"
                : "Projected scenario only · no profile changes or verified skill gains"}
            </footer>
          </section>
          <section className="card">
            <div className="section-heading">
              <div>
                <div className="eyebrow">A MORE USEFUL NEXT STEP</div>
                <h2>Prioritize your possibilities.</h2>
              </div>
              <select
                aria-label="Rank recommendations"
                value={rank}
                onChange={(e) => setRank(e.target.value)}
              >
                <option value="match">Sort by JD-fit gain</option>
                <option value="readiness">Sort by readiness gain</option>
              </select>
            </div>
            {recommendations.slice(0, 8).map((item: any, i: number) => (
              <div className="recommendation" key={`${item.action}-${i}`}>
                <span className="recommendation-index">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <strong>{item.action}</strong>
                  <p>
                    {item.type === "evidence"
                      ? "Clarify evidence; no automatic score gain"
                      : item.reason}
                  </p>
                </div>
                {item.type === "capability" && (
                  <button
                    className="button small"
                    onClick={() => {
                      if (item.skill_name)
                        setSkills([...new Set([...skills, item.skill_name])]);
                      else if (item.target_level)
                        setLevels({
                          ...levels,
                          [item.category_code]: item.target_level,
                        });
                    }}
                  >
                    Try it
                  </button>
                )}
                <span className="gain">
                  {item[rank === "match" ? "match_delta" : "readiness_delta"] !=
                  null
                    ? `+${item[rank === "match" ? "match_delta" : "readiness_delta"]} pts`
                    : "Assess first"}
                </span>
              </div>
            ))}
            <p className="fine-print">
              Each gain is a separate single-change projection from the
              baseline. Gains may overlap and should not be added. No
              learning-time or hiring guarantee is implied.
            </p>
          </section>
        </>
      )}
    </>
  );
}
