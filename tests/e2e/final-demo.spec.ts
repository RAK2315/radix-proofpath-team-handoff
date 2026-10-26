import { test, expect } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

const codes = [
  "COD",
  "DSA",
  "OOD",
  "APTI",
  "COMM",
  "AI",
  "CLOUD",
  "SQL",
  "SWE",
  "SYSD",
  "NETW",
  "OS",
];
test("final synthetic Mira demo: real uploads, review, receipt chain, two scores and reset", async ({
  page,
  request,
}) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const screenshots = resolve("demo/final/screenshots");
  mkdirSync(screenshots, { recursive: true });
  await page.goto("/#jd");
  await page.locator("input[type=file]:visible").setInputFiles({
    name: "invalid.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("This is not a PDF file."),
  });
  await expect(page.getByRole("alert")).toContainText("PDF signature");
  await page
    .locator("input[type=file]:visible")
    .setInputFiles(
      resolve("demo/final/junior-data-engineer-jd-SYNTHETIC.docx"),
    );
  await expect(page.getByLabel("Role", { exact: true })).toHaveValue(
    "Junior Data Engineer (synthetic)",
  );
  await expect(page.getByLabel("Requirement 1 importance")).toHaveValue(
    "mandatory",
  );
  await expect(page.getByLabel("Requirement 5 operator")).toHaveValue("OR");
  await page
    .getByRole("button", { name: "Inspect requirement wording and source" })
    .first()
    .click();
  await expect(page.getByRole("dialog")).toContainText(
    "You must know Python and SQL",
  );
  await page.getByRole("button", { name: "Close evidence" }).click();
  await page.getByRole("button", { name: "Save reviewed JD" }).click();
  await expect(
    page.getByText("Reviewed · ready for matching", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Parse your resume", exact: true })
    .click();
  await page
    .locator("input[type=file]:visible")
    .setInputFiles(resolve("demo/final/mira-cv-SYNTHETIC.pdf"));
  await expect(page.getByLabel("Extracted projects")).toContainText(
    "fictional parcel records",
  );
  await expect(page.getByLabel("Extracted internships")).toContainText(
    "training placement",
  );
  // Deliberately exercise a human correction; do not claim the parser made this category error.
  await page
    .getByLabel("Category for Python", { exact: true })
    .filter({ visible: true })
    .selectOption("AI");
  await page
    .getByLabel("Category for Python", { exact: true })
    .filter({ visible: true })
    .selectOption("COD");
  await page.getByRole("button", { name: "Save reviewed resume" }).click();
  await expect(page.locator(".toast")).toContainText("Resume review saved");
  await page
    .getByRole("button", { name: "Build your profile", exact: true })
    .click();
  await page.getByRole("button", { name: "Import", exact: true }).click();
  await expect(page.getByLabel("Full name")).toHaveValue(
    "Mira Sen (synthetic)",
  );
  for (const code of codes) {
    await expect(
      page.getByLabel(`${code} competency`, { exact: true }),
    ).toHaveValue("");
    await page
      .getByLabel(`${code} competency`, { exact: true })
      .selectOption("4");
  }
  await page.getByRole("button", { name: "Save profile", exact: true }).click();
  await expect(
    page.getByText(/Editing saved profile · revision/),
  ).toBeVisible();
  const id = await page.getByLabel("Selected candidate").inputValue();
  const before = await (await request.get(`/api/profiles/${id}`)).json();
  expect(before.skills).toHaveLength(6);
  await page.reload();
  await expect(page.getByLabel("Full name")).toHaveValue(
    "Mira Sen (synthetic)",
  );
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /Talent Check/ })
    .click();
  await page.getByLabel("Benchmark data mode").selectOption("synthetic");
  await expect(page.getByLabel("Selected company")).toContainText(
    "Synthetic Data Co",
  );
  await page.getByLabel("Selected company").selectOption("lab-data");
  await page
    .getByRole("button", { name: "Run Talent Check", exact: true })
    .click();
  await expect(page.locator(".readiness-score .score")).toContainText("74.9");
  await expect(page.locator(".comparison-row")).toHaveCount(12);
  await page.screenshot({
    path: resolve(screenshots, "01-readiness.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "See your JD match", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Analyze this match", exact: true })
    .click();
  await expect(page.locator(".match-summary .score")).toContainText("75.0");
  await expect(page.locator(".gps .projected-score")).toHaveText("75%");
  await page.getByRole("button", { name: "Matched 4", exact: true }).click();
  await page.locator(".decision-row").filter({ hasText: "Python" }).click();
  const chain = page.getByRole("region", { name: "ProofPath reasoning chain" });
  await expect(chain).toContainText("You must know Python and SQL");
  await expect(chain).toContainText("Python, SQL, Pandas, NumPy, Git, Linux");
  await expect(chain).toContainText("12.50 points out of 100");
  await expect(chain).toContainText("unverified");
  await page.screenshot({
    path: resolve(screenshots, "02-proofpath-chain.png"),
  });
  await page.setViewportSize({ width: 390, height: 1000 });
  expect(
    await page
      .getByRole("dialog")
      .evaluate((element) => element.scrollWidth <= element.clientWidth),
  ).toBe(true);
  await page.screenshot({ path: resolve(screenshots, "05-mobile-chain.png") });
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.getByRole("button", { name: "Close evidence" }).click();
  await page
    .getByRole("button", { name: "Evidence gaps 3", exact: true })
    .click();
  await page.locator(".decision-row").filter({ hasText: "Docker" }).click();
  await expect(chain).toContainText("No equivalent reviewed claim");
  await expect(chain).toContainText("0.00 points out of 100");
  await page.getByRole("button", { name: "Explore in Career GPS" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("checkbox", { name: /Docker Hypothetical/ }).check();
  await expect(page.locator(".gps .projected-score")).toHaveText("87.5%");
  await page
    .getByRole("slider", { name: "SQL hypothetical level", exact: true })
    .fill("9");
  await expect(page.locator(".gps-scores")).toContainText("79.5");
  await page.getByRole("checkbox", { name: /AWS Hypothetical/ }).check();
  await expect(page.locator(".gps .projected-score")).toHaveText("100%");
  await page.screenshot({
    path: resolve(screenshots, "03-combined-scenario.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Reset scenario" }).click();
  await expect(page.locator(".gps .projected-score")).toHaveText("75%");
  await expect(page.locator(".gps-scores")).toContainText("74.9");
  expect(await (await request.get(`/api/profiles/${id}`)).json()).toEqual(
    before,
  );
  // An actual reviewed JD edit changes subsequent evaluations; the saved profile stays fixed.
  const jdId = await page.getByLabel("Selected job").inputValue();
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /JD Analytics/ })
    .click();
  await page.getByLabel("Requirement 4 importance").selectOption("mandatory");
  await page.getByRole("button", { name: "Save reviewed JD" }).click();
  await expect(
    page.getByText("Reviewed · ready for matching", { exact: true }),
  ).toBeVisible();
  const revised = await request.post("/api/matching/evaluate", {
    headers: { "X-ProofPath-Client": "final-demo-test" },
    data: { profile_id: id, jd_id: jdId },
  });
  expect((await revised.json()).match_score).toBe(66.7);
  await page.getByLabel("Requirement 4 importance").selectOption("preferred");
  await page.getByRole("button", { name: "Save reviewed JD" }).click();
  await expect(
    page.getByText("Reviewed · ready for matching", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "See your JD match", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Analyze this match", exact: true })
    .click();
  await expect(page.locator(".gps .projected-score")).toHaveText("75%");
  await expect(page.locator(".toast")).toHaveCount(0, { timeout: 10000 });
  await page.setViewportSize({ width: 390, height: 1000 });
  await page.screenshot({
    path: resolve(screenshots, "04-mobile-match.png"),
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});

test("unfamiliar unparsed technologies stay provisional until explicit source review", async ({
  page,
  request,
}) => {
  const profile = await (
    await request.post("/api/profiles", {
      headers: { "X-ProofPath-Client": "unparsed-test" },
      data: {
        name: "Synthetic incomplete-coverage test",
        skills: [{ skill_name: "Python", category_code: "COD" }],
      },
    })
  ).json();
  await page.goto("/#jd");
  await page.getByLabel("Selected candidate").selectOption(profile.id);
  await page.getByRole("tab", { name: "Paste text" }).click();
  await page
    .getByLabel("Job description text")
    .fill(
      "Company: Synthetic Unfamiliar Co\nRole: Integration Engineer\nRequirements\n- Python and Rust\n- Apache Arrow",
    );
  await page.getByRole("button", { name: "Extract pasted JD" }).click();
  await expect(
    page.getByText("Check missing requirements before scoring"),
  ).toBeVisible();
  await page.getByRole("button", { name: "Save reviewed JD" }).click();
  await expect(
    page.getByText("Reviewed · ready for matching", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "See your JD match", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Analyze this match", exact: true })
    .click();
  await expect(page.locator(".match-summary > .pill")).toHaveText(
    "provisional",
  );
  await expect(
    page.getByRole("button", { name: "Review JD coverage" }),
  ).toBeVisible();
});
