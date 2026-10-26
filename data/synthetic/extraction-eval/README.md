# Unfamiliar extraction development set

All 12 source documents in [cases.json](cases.json) are invented. Six resumes and six JDs are rendered as both PDF and DOCX, making **24 document-format observations**. The two formats represent the same content, not independent people or jobs. Expected named skills, selected field substrings, claim-review flags and requirement groups were specified before the first run. The set was then used to fix defects; it is not held out, independent or an organizer acceptance benchmark.

Generate files with `python -m scripts.evaluation_documents` from the virtualenv. Run `python -m scripts.evaluate_extraction` to regenerate the current results in `docs/evaluation/final.json`. The initial output is preserved in `docs/evaluation/baseline.json`.

Scope includes banner-first resumes, explicit names, portfolio URLs, skills with overlapping names, action aliases, negation, unfamiliar sections, table-based DOCX/two-column PDF, alternate job headings, required/preferred duplicates, mixed AND/OR and contradictory wording, incomplete JDs and unfamiliar technologies. Source quotes must validate against the extracted page text. Two-column reconstruction is deliberately conservative and produces a review warning.

Precision = TP/(TP+FP); recall = TP/(TP+FN), where TP/FP/FN compare the set of extracted **named mentions** with the explicit expected skill set for each document-format. Negated mentions count as expected extractions only with a separate `needs_review` flag; they are not accepted ability claims. There is no competency-accuracy metric.

| Run | TP | FP | FN | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Initial parser | 80 | 2 | 22 | 97.56% | 78.43% |
| Corrected development parser | 94 | 0 | 8 | 100% | 92.16% |

The eight misses are four underlying expectations repeated in both formats: Rust and implicit Data Cleaning in one CV; Rust and Apache Arrow in one JD. These remain unsupported. They have not been removed from the denominator or invented as supported outputs. Unparsed JD warnings keep recognized-group scores provisional; the review UI requires an explicit coverage acknowledgement and group correction. The capitalization warning is heuristic and cannot detect every unknown lowercase technology or implicit requirement.

Expected groups pass for all ten document-format cases with complete group gold labels. The unknown-technology JD intentionally has no complete group score gold label: its source warns about missing coverage. Name and selected section assertions pass where defined. Synthetic source PDFs were rendered for inspection, not just text-dumped; test images remain under ignored `test-results/final-pdf-review/`.
