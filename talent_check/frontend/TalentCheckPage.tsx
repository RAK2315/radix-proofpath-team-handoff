import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, Database, RefreshCw } from "lucide-react";
import { post } from "../../shared/ui/api";
import { useWorkspace } from "../../shared/ui/context";
import {
  Empty,
  NextButton,
  Notice,
  PageTitle,
  Score,
} from "../../shared/ui/components";
export default function TalentCheckPage() {
  const w = useWorkspace();
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [active, setActive] = useState("all");
  const selectionKey = `${w.profile?.id}:${w.profile?.revision}:${w.company?.id}:${w.mode}`;
  const activeKey = useRef(selectionKey);
  activeKey.current = selectionKey;
  useEffect(() => {
    setResult(null);
    setBusy(false);
    setError("");
  }, [w.profile?.id, w.profile?.revision, w.company?.id, w.mode]);
  async function evaluate() {
    setBusy(true);
    setError("");
    try {
      const value = await post("/talent-check/evaluate", {
        profile_id: w.profile?.id,
        company_id: w.company?.id,
        benchmark_mode: w.mode,
      });
      if (activeKey.current === selectionKey) setResult(value);
    } catch (e) {
      if (activeKey.current === selectionKey) setError((e as Error).message);
    } finally {
      if (activeKey.current === selectionKey) setBusy(false);
    }
  }
  const rows =
    result?.skillset_gap.filter(
      (r: any) =>
        active === "all" ||
        (active === "gaps" ? r.gap : r.status === "unknown"),
    ) || [];
  return (
    <>
      <PageTitle
        eyebrow="04 / MEASURE COMPANY READINESS"
        title="Know where you stand."
        description="A transparent comparison against a company’s expectations across all 12 RADIX categories."
        action={
          <button
            className="button primary"
            disabled={!w.profile || !w.company || busy}
            onClick={() => void evaluate()}
          >
            <RefreshCw size={16} />
            {busy ? "Comparing…" : "Run Talent Check"}
          </button>
        }
      />
      {!result && (
        <section className="card route-help">
          <div>
            <strong>Want to compare your CV with a specific JD?</strong>
            <p>
              Use Skill Matching for that result. Talent Check needs company
              benchmarks and your twelve self-ratings.
            </p>
          </div>
          <button
            className="button primary"
            onClick={() => w.navigate("matching")}
          >
            Compare CV with JD <ArrowUpRight size={16} />
          </button>
        </section>
      )}
      {error && <Notice tone="error">{error}</Notice>}
      <div className="section-bar benchmark-refresh">
        <p className="fine-print">
          Benchmarks are cached for 15 minutes. Refresh to fetch a new validated
          snapshot.
        </p>
        <button
          className="button small"
          onClick={async () => {
            try {
              await w.refreshCompanies();
              setResult(null);
              w.notify("Company data refreshed. Run Talent Check again.");
            } catch (error) {
              setError((error as Error).message);
            }
          }}
        >
          <RefreshCw size={13} /> Refresh company data
        </button>
      </div>
      {w.mode === "synthetic" && !result && (
        <Notice tone="lab">
          SYNTHETIC LAB · Company names and competency levels are invented
          testing fixtures. These are not official RADIX benchmarks.
        </Notice>
      )}
      {!w.profile ? (
        <Empty
          title="Start with a saved profile."
          description="Talent Check uses explicit self-ratings from Profile Builder. Resume keywords never become ability levels automatically."
          onClick={() => w.navigate("profile")}
          label="Build a profile"
        />
      ) : !w.company ? (
        <section className="card">
          <Empty
            title="Connect the company benchmark source."
            description="Real scoring requires Supabase staging_company_skill_levels or a genuine export. No benchmark values have been fabricated."
          />
          <div className="center">
            <button className="button" onClick={() => w.setMode("synthetic")}>
              Explore explicitly synthetic lab data
            </button>
          </div>
        </section>
      ) : result ? (
        <>
          <div className="readiness-summary">
            <section className="card readiness-score">
              <div>
                <div className="eyebrow">{result.company}</div>
                <Score
                  value={result.readiness_score}
                  label="Profile-based readiness estimate"
                />
                <p>
                  {result.status === "incomplete"
                    ? `Assess ${12 - result.rating_completeness} remaining categories for a final score.`
                    : "Self-reported competency · all 12 categories assessed"}
                </p>
              </div>
              <div className="score-orbit">
                <span>
                  {result.rating_completeness}
                  <small>/12 assessed</small>
                </span>
              </div>
            </section>
            <section className="card source-card">
              <Database size={22} />
              <h3>Grounded in a visible source.</h3>
              <dl>
                <dt>Data mode</dt>
                <dd>{result.benchmark_source.source_mode}</dd>
                <dt>Source table</dt>
                <dd>{result.benchmark_source.source_table}</dd>
                <dt>Fetched</dt>
                <dd>
                  {result.benchmark_source.fetched_at
                    ? new Date(
                        result.benchmark_source.fetched_at,
                      ).toLocaleString()
                    : "Synthetic fixture"}
                </dd>
                <dt>Evidence-linked categories</dt>
                <dd>
                  {result.evidence_coverage} / 12 · links do not verify ability
                </dd>
              </dl>
              {result.benchmark_source.notice && (
                <Notice>{result.benchmark_source.notice}</Notice>
              )}
              <button
                className="text-button"
                onClick={() => w.showReceipt(result.receipt_id)}
              >
                Inspect decision receipt <ArrowUpRight size={14} />
              </button>
            </section>
          </div>
          <section className="card">
            <div className="section-heading">
              <div>
                <h2>Your 12-skill comparison</h2>
                <p className="muted">
                  Select a row to follow the evidence and see the arithmetic.
                </p>
              </div>
              <div className="segmented">
                {[
                  ["all", "All 12"],
                  ["gaps", "Gaps"],
                  ["unknown", "Unknown"],
                ].map(([id, name]) => (
                  <button
                    key={id}
                    className={active === id ? "selected" : ""}
                    onClick={() => setActive(id)}
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>
            <div className="chart-legend">
              <span>
                <i className="legend-candidate" />
                Your self-rating
              </span>
              <span>
                <i className="legend-required" />
                Company expectation
              </span>
            </div>
            <div className="category-comparison">
              {rows.map((row: any) => (
                <button
                  className="comparison-row"
                  key={row.category_code}
                  onClick={() => w.showEvidence(row)}
                >
                  <div className="comparison-label">
                    <b>{row.category_code}</b>
                    <span>{row.category_name}</span>
                  </div>
                  <div className="bar-pair">
                    <div className="bar-track">
                      <span
                        className="candidate-bar"
                        style={{ width: `${(row.candidate_level || 0) * 10}%` }}
                      />
                    </div>
                    <div className="bar-track">
                      <span
                        className="required-bar"
                        style={{ width: `${row.required_level * 10}%` }}
                      />
                    </div>
                  </div>
                  <div className="comparison-number">
                    {row.candidate_level ?? "?"}{" "}
                    <span>/ {row.required_level}</span>
                  </div>
                  <span className={`gap-label ${row.status}`}>
                    {row.status === "unknown"
                      ? "Unassessed"
                      : row.gap
                        ? `Gap ${row.shortfall}`
                        : row.status === "above_expected"
                          ? "Above"
                          : "Meets"}
                  </span>
                </button>
              ))}
            </div>
            <details className="methodology">
              <summary>How this score is calculated</summary>
              <p>{result.methodology}</p>
              <code>100 × mean(min(candidate_level / required_level, 1))</code>
              <p>
                Each category contributes at most 1/12 of the score. Unknown
                categories block the final percentage. Confidence and evidence
                coverage are displayed separately.
              </p>
            </details>
          </section>
          <div className="next-step">
            <p>
              Company readiness is one view. Now explore your fit for the actual
              job.
            </p>
            <NextButton onClick={() => w.navigate("matching")}>
              See your JD match
            </NextButton>
          </div>
        </>
      ) : (
        <section className="card">
          <Empty
            title={`${w.profile.name} × ${w.company.name}`}
            description="Run Talent Check to reveal category-level attainment, skill gaps and source-linked explanations."
            onClick={() => void evaluate()}
            label="Compare all 12 categories"
          />
        </section>
      )}
    </>
  );
}
