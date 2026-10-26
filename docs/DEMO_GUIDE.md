# Reproducible five-module demonstration

All sources in this procedure are invented. The five-module Mira flow was executed by
`tests/e2e/final-demo.spec.ts`. It is separate from the overview's older synthetic Alpha walkthrough.
Use the exact files and candidate/job below to reproduce these numbers.

## Start

Follow root README installation, then run two terminals from the repository root:

```powershell
# Terminal 1
$env:RADIX_LLM_MODE='rules'
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
# Terminal 2
npm run dev
```

Open http://127.0.0.1:5173/. Use the normal integrated app, not a selected-feature host. Do not click
the older overview walkthrough and assume its numbers should equal Mira's.

## Live procedure: approximately ten minutes

1. **JD Analytics:** upload `demo/final/junior-data-engineer-jd-SYNTHETIC.docx`.
   Check Junior Data Engineer (synthetic), five groups and the exact quote **You must know Python and SQL**.
   Python+SQL, Pandas and Linux are mandatory; Docker and AWS OR GCP are preferred. Open source evidence,
   explain AND versus OR and save reviewed JD. Optionally show paste input with a separate labelled JD,
   then select the Mira JD again before assessment.
2. **Resume Parsing:** upload `demo/final/mira-cv-SYNTHETIC.pdf`. Check six claims: Python, SQL, Pandas,
   NumPy, Git and Linux; fictional parcel project and training placement. Open the original quote.
   Demonstrate a deliberate human category correction, then save reviewed resume. A quote supports a
   claim; it does not prove measured proficiency.
3. **Profile Builder:** import that reviewed resume. Show name, education, project, internship and other
   editable background fields. Confirm all twelve ratings initially remain Unknown. For this synthetic
   numerical demonstration only, deliberately set all twelve to **4**. Save, reload and show persistence.
   These numbers are invented inputs, not parser inferences. Add a harmless preferred role and save again
   if demonstrating manual edits.
4. **Talent Check:** select **Synthetic lab** mode and **Synthetic Data Co** (`lab-data`). Run Talent Check:
   **74.9%**, twelve rows, 12/12 assessed. Inspect SQL: level 4 versus expected 9, shortfall 5 and 3.7037
   contribution points. Explain the equal-weight capped attainment calculation. Clear a rating only if
   demonstrating the incomplete state, then restore/save 4 before continuing. Real source mode must show
   unavailable configuration; it must never display lab values as official.
5. **Skill Matching:** select Mira and the saved Junior Data Engineer JD, then **Analyze this match**.
   Expect **75.0%**. Open Matched 4 -> Python. Show JD quote -> CV claim quote -> unverified claim status
   -> **12.50 points out of 100** -> action. Open the Docker evidence gap: no equivalent reviewed claim,
   zero contribution. These are separate named-skill coverage and company self-rating calculations.
6. **Career GPS:** check hypothetical Docker: match **87.5%**, company readiness stays **74.9%**.
   Move hypothetical SQL level to **9**: readiness **79.5%**, match stays **87.5%**.
   Check hypothetical AWS: match **100%**, because one member satisfies AWS OR GCP. Explain these are
   reversible scenarios, not certifications or guaranteed future performance.
7. **Reset scenario:** baseline returns to **75% / 74.9%**. Return to the saved profile: SQL is still 4;
   Docker/AWS were not added. Profile JSON before/after is identical in the automated check.
8. **Failure/recovery:** upload text renamed `invalid.pdf` in JD Analytics and show the PDF signature error,
   then upload the valid fixture. Show Unknown ratings or unavailable real benchmarks as honest states.
   If demonstrating JD edits, changing Docker to mandatory gives **66.7%** after saved re-evaluation;
   restore preferred and re-evaluate to return to 75%. Old receipts are invalidated after edits.

## Independent teammate demonstrations

Stop the integrated servers before using the same ports. From root, run `MODULE/run.ps1 api` and
`MODULE/run.ps1 web` in separate terminals, then use **Load synthetic inputs** where upstream records are
needed. This supplies pre-reviewed snapshots, not fresh LLM extraction. Each START_HERE guide's test
section gives its live checks, and its final section gives a 45-second explanation and judge questions.
Each teammate must demonstrate their own tested checkout and return its SHA.

## Automated rehearsal and evidence

```powershell
npm run test:e2e
npm run test:handoff
```

The former runs nine integrated browser checks including this full Mira journey; the latter runs five
separate module hosts. Actual counts and known parser misses are in `../verification/RESULTS.md`.
Screenshots contain only synthetic information. Do not show private keys, real CV data or claim that
live Groq/Supabase/official datasets were verified. Rehearse with the actual five speakers and confirm
your organizer-assigned presentation slot.
