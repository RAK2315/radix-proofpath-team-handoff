import { expect, test } from "@playwright/test";

test("cloud sign-in and owner workspace load without a local Vite proxy", async ({
  page,
}) => {
  test.skip(
    !process.env.RADIX_CLOUD_TEST_EMAIL ||
      !process.env.RADIX_CLOUD_TEST_PASSWORD,
    "Requires an authorized synthetic test account",
  );
  await page.goto("/");
  await page
    .getByLabel("Email", { exact: true })
    .fill(process.env.RADIX_CLOUD_TEST_EMAIL!);
  await page
    .getByLabel("Password", { exact: true })
    .fill(process.env.RADIX_CLOUD_TEST_PASSWORD!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("navigation")).toBeVisible();
  await expect(
    page.getByRole("button", { name: /JD Analytics/ }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: /Sign out/ }).click();
  await expect(
    page.getByRole("button", { name: "Sign in", exact: true }),
  ).toBeVisible();
});
