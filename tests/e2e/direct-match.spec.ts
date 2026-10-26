import { test, expect } from "@playwright/test";

test("CV to JD comparison works with unknown ratings and no company benchmarks", async ({
  page,
  request,
}) => {
  const response = await request.post("/api/profiles", {
    headers: { "X-ProofPath-Client": "direct-match-test" },
    data: {
      name: "Synthetic ML candidate",
      skills: ["Python", "Pandas", "NumPy", "scikit-learn", "PyTorch"].map(
        (skill_name) => ({
          skill_name,
          category_code: skill_name === "Python" ? "COD" : "AI",
        }),
      ),
    },
  });
  expect(response.ok()).toBeTruthy();
  const profile = await response.json();
  await page.goto("/#jd");
  await page
    .getByRole("combobox", { name: "Selected candidate" })
    .selectOption(profile.id);
  await page.getByRole("tab", { name: "Paste text" }).click();
  await page
    .getByLabel("Job description text")
    .fill(
      "About the job\nMachine Learning Intern\nCompany: Synthetic internship employer\nRequirements\n- Familiarity with Python programming.\n- Pandas, NumPy, and scikit-learn is an advantage.\n- TensorFlow, PyTorch, or Deep Learning is a plus.",
    );
  await page.getByRole("button", { name: "Extract pasted JD" }).click();
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
  await expect(page.locator(".match-summary .score")).toContainText("100.0");
  await expect(page.getByText(/An evidence gap means/)).toBeVisible();
  await expect(page.locator(".gps .projected-score")).toHaveText("100%");
  expect(
    profile.ratings.every((r: { level: number | null }) => r.level === null),
  ).toBe(true);
  await expect(
    page.getByRole("combobox", { name: "Selected company" }),
  ).not.toBeVisible();
  await page
    .locator(".sidebar")
    .getByRole("button", { name: /Talent Check/ })
    .click();
  await page.getByRole("button", { name: "Compare CV with JD" }).click();
  await expect(
    page.getByRole("heading", { name: "Your match, explained." }),
  ).toBeVisible();
});
