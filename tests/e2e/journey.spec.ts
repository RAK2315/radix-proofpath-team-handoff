import { test, expect } from "@playwright/test";

test("upload, review, import, persistence, all 12 comparisons, evidence and reversible GPS", async ({
  page,
  request,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Your potential/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "CV to job comparison" }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("status")
      .filter({ hasText: /Real company benchmarks need/ }),
  ).not.toBeVisible();
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /JD Analytics/ })
    .click();
  const job = await request.get("/api/examples/jd/0");
  await page.locator("input[type=file]:visible").setInputFiles({
    name: "synthetic-job.docx",
    mimeType:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    buffer: await job.body(),
  });
  await expect(
    page.getByRole("heading", { name: "Review the requirements" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Save reviewed JD" }).click();
  await expect(
    page.getByText("Reviewed · ready for matching", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Parse your resume", exact: true })
    .click();
  const resume = await request.get("/api/examples/resumes/0");
  await page.locator("input[type=file]:visible").setInputFiles({
    name: "synthetic-resume.docx",
    mimeType:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    buffer: await resume.body(),
  });
  await expect(
    page.getByRole("heading", { name: "Review your extracted profile" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Save reviewed resume" }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "Resume review saved." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Build your profile", exact: true })
    .click();
  await page.getByRole("button", { name: "Import", exact: true }).click();
  await expect(page.getByRole("textbox", { name: "Full name" })).toHaveValue(
    "Synthetic Candidate Alpha",
  );
  await page
    .getByRole("textbox", { name: "Full name" })
    .fill("Synthetic Browser Candidate");
  for (const code of [
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
  ])
    await page
      .getByRole("combobox", { name: `${code} competency`, exact: true })
      .selectOption("4");
  await page.getByRole("button", { name: "Save profile", exact: true }).click();
  await expect(
    page.getByText(/Editing saved profile · revision/),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByRole("textbox", { name: "Full name" })).toHaveValue(
    "Synthetic Browser Candidate",
  );
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /Talent Check/ })
    .click();
  await page
    .getByRole("combobox", { name: "Benchmark data mode" })
    .selectOption("synthetic");
  await expect(
    page.getByRole("combobox", { name: "Selected company" }),
  ).toContainText("Synthetic Systems Co");
  await page
    .getByRole("combobox", { name: "Selected company" })
    .selectOption("lab-systems");
  await page
    .getByRole("button", { name: "Run Talent Check", exact: true })
    .click();
  await expect(page.locator(".comparison-row")).toHaveCount(12);
  await page.locator(".comparison-row").filter({ hasText: "Coding" }).click();
  await expect(page.getByRole("dialog")).toContainText("Score contribution");
  await page
    .getByRole("dialog")
    .getByRole("button", { name: /Python/ })
    .click();
  await expect(page.getByRole("dialog")).toContainText("synthetic-resume.docx");
  await page.getByRole("button", { name: "Close evidence" }).click();
  await page.getByRole("button", { name: "See your JD match" }).click();
  await page
    .getByRole("button", { name: "Analyze this match", exact: true })
    .first()
    .click();
  await expect(page.locator(".gps")).toBeVisible();
  await expect(page.locator(".gps footer")).toContainText("no profile changes");
  await expect(page.locator(".gps .projected-score")).toHaveText(/\d/);
  const baseline = await page.locator(".gps .projected-score").innerText();
  await page.getByRole("checkbox", { name: /Docker/ }).check();
  await expect(page.locator(".gps .projected-score")).not.toHaveText(baseline);
  await page
    .getByRole("slider", { name: "COD hypothetical level", exact: true })
    .fill("8");
  await expect(page.locator(".gps footer")).toContainText("no profile changes");
  await page.getByRole("button", { name: "Reset scenario" }).click();
  await expect(page.locator(".gps .projected-score")).toHaveText(baseline);
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /Profile Builder/ })
    .click();
  await expect(
    page.getByRole("combobox", { name: "COD competency", exact: true }),
  ).toHaveValue("4");
  await expect(
    page.getByRole("textbox", { name: "Skill name" }).filter({ visible: true }),
  ).toHaveCount(4);
  expect(errors).toEqual([]);
});

test("synthetic walkthrough and responsive navigation", async ({ page }) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: /Explore a synthetic walkthrough/ })
    .click();
  await expect(page.locator(".lab-ribbon")).toBeVisible();
  await expect(
    page.getByRole("combobox", { name: "Selected candidate" }),
  ).not.toHaveValue("");
  await page.screenshot({
    path: "test-results/overview-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /Skill Matching/ })
    .click();
  await expect(
    page.getByRole("heading", { name: "Find your path forward." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Analyze this match", exact: true })
    .first()
    .click();
  await expect(page.locator(".gps")).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
    )
    .toBe(true);
  await page.screenshot({
    path: "test-results/matching-mobile.png",
    fullPage: true,
  });
});

test("cloud auth gates candidate content and explains missing frontend configuration", async ({
  page,
}) => {
  await page.route("**/api/status", (route) =>
    route.fulfill({
      json: {
        auth_mode: "supabase",
        storage_mode: "supabase",
        llm_configured: false,
      },
    }),
  );
  await page.route("**/api/documents", (route) =>
    route.fulfill({
      status: 401,
      json: { code: "AUTH_REQUIRED", message: "Synthetic login required" },
    }),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Your private workspace." }),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toContainText(
    "Cloud sign-in is not configured",
  );
  await expect(page.getByRole("navigation")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: /Data & privacy/ }),
  ).toHaveCount(0);
});
