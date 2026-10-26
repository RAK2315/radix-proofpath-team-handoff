import { expect, test } from "@playwright/test";
import { resolve } from "node:path";

test("independent feature performs its real workflow and fits a mobile viewport", async ({
  page,
  request,
}, info) => {
  const module = info.project.name;
  await page.goto("/");
  await page.getByRole("button", { name: "Load synthetic inputs" }).click();
  await expect(
    page.getByLabel("Candidate profile", { exact: true }),
  ).toContainText("Mira Sen");
  if (module === "jd_analytics") {
    await page.getByRole("tab", { name: "Paste text" }).click();
    await page
      .getByLabel("Job description text")
      .fill(
        "Company: Synthetic Test Co\nRole: API Engineer\nRequired: Python and SQL\nPreferred: Docker",
      );
    await page.getByRole("button", { name: "Extract pasted JD" }).click();
    await expect(
      page.getByRole("heading", { name: "Review the requirements" }),
    ).toBeVisible();
    await page.getByRole("button", { name: "Save reviewed JD" }).click();
    await expect(
      page.getByText("Reviewed · ready for matching", { exact: true }),
    ).toBeVisible();
  } else if (module === "resume_parsing") {
    await page
      .getByLabel("Upload document")
      .setInputFiles(resolve("demo/final/mira-cv-SYNTHETIC.pdf"));
    await expect(
      page.getByRole("button", { name: "Save reviewed resume" }),
    ).toBeVisible();
    await expect(page.getByLabel("Extracted projects")).toContainText("Python");
    await page.getByRole("button", { name: "Save reviewed resume" }).click();
    await expect(
      page.getByText("Resume review saved. Import it from Profile Builder."),
    ).toBeVisible();
  } else if (module === "profile_builder") {
    await page
      .getByRole("button", { name: "New profile", exact: true })
      .click();
    await page.getByRole("button", { name: "Import", exact: true }).click();
    await expect(page.getByLabel("Full name")).toHaveValue(
      "Mira Sen (synthetic)",
    );
    await expect(
      page.getByLabel("COD competency", { exact: true }),
    ).toHaveValue("");
    await page
      .getByRole("button", { name: "Save profile", exact: true })
      .click();
    await expect(page.getByText(/Saved · v/)).toBeVisible();
    await page.reload();
    await expect(page.getByLabel("Full name")).not.toHaveValue("");
  } else if (module === "talent_check") {
    await page
      .getByRole("button", { name: "Run Talent Check", exact: true })
      .click();
    await expect(page.locator(".readiness-score .score")).toContainText("74.9");
    await expect(page.locator(".comparison-row")).toHaveCount(12);
  } else {
    const before = await (await request.get("/api/handoff/context")).json();
    await page
      .getByRole("button", { name: "Analyze this match", exact: true })
      .click();
    await expect(page.locator(".match-summary .score")).toContainText("75.0");
    await page.getByRole("button", { name: "Matched 4", exact: true }).click();
    await page.locator(".decision-row").filter({ hasText: "Python" }).click();
    await expect(
      page.getByRole("region", { name: "ProofPath reasoning chain" }),
    ).toContainText("12.50");
    await page.getByRole("button", { name: "Close evidence" }).click();
    await page.getByRole("checkbox", { name: /Docker Hypothetical/ }).check();
    await expect(page.locator(".gps .projected-score")).toHaveText("87.5%");
    await page.getByRole("button", { name: "Reset scenario" }).click();
    await expect(page.locator(".gps .projected-score")).toHaveText("75%");
    expect(
      (await (await request.get("/api/handoff/context")).json()).profiles,
    ).toEqual(before.profiles);
  }
  await page.setViewportSize({ width: 390, height: 1000 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: `verification/local/${module}-mobile.png`,
    fullPage: true,
  });
});
