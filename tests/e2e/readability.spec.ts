import { test, expect } from "@playwright/test";

test("semantic text colours and comparison bars meet their contrast targets", async ({
  page,
}) => {
  await page.goto("/");
  const contrasts = await page.evaluate(() => {
    const style = getComputedStyle(document.documentElement);
    const token = (name: string) => style.getPropertyValue(name).trim();
    const luminance = (hex: string) => {
      const raw = hex.replace("#", "");
      const colour =
        raw.length === 3
          ? raw
              .split("")
              .map((x) => x + x)
              .join("")
          : raw;
      const linear = [0, 2, 4]
        .map((i) => parseInt(colour.slice(i, i + 2), 16) / 255)
        .map((n) => (n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4));
      return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
    };
    const ratio = (a: string, b: string) => {
      const levels = [luminance(a), luminance(b)].sort((a, b) => a - b);
      return (levels[1] + 0.05) / (levels[0] + 0.05);
    };
    const textPairs = [
      ["--text", "--surface"],
      ["--muted", "--canvas"],
      ["--accent", "--surface"],
      ["--surface", "--accent"],
      ["--success", "--success-soft"],
      ["--warning", "--warning-soft"],
      ["--danger", "--danger-soft"],
    ];
    return [
      ...textPairs.map(([a, b]) => ({
        pair: `${a} / ${b}`,
        ratio: ratio(token(a), token(b)),
        minimum: 4.5,
      })),
      {
        pair: "Company bar / track",
        ratio: ratio(token("--benchmark-bar"), token("--bar-track")),
        minimum: 3,
      },
    ];
  });
  for (const item of contrasts)
    expect(item.ratio, item.pair).toBeGreaterThanOrEqual(item.minimum);
});

test("all screens keep readable text, bundled fonts and responsive layouts", async ({
  page,
}) => {
  const externalFonts: string[] = [];
  page.on("request", (request) => {
    if (/fonts\.googleapis|fonts\.gstatic|rsms\.me/.test(request.url()))
      externalFonts.push(request.url());
  });
  await page.goto("/");
  await page
    .getByRole("button", { name: /Explore a synthetic walkthrough/ })
    .click();
  await expect(page.locator(".lab-ribbon")).toBeVisible();
  await expect(page.locator(".toast")).toHaveCount(0, { timeout: 10000 });
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const view of [
      "overview",
      "jd",
      "resume",
      "profile",
      "talent",
      "matching",
    ]) {
      await page.goto(`/#${view}`);
      await page
        .getByRole("heading", { level: 1 })
        .filter({ visible: true })
        .waitFor();
      if (view === "talent") {
        await page
          .getByRole("button", { name: "Run Talent Check", exact: true })
          .click();
        await expect(page.locator(".comparison-row")).toHaveCount(12);
      }
      if (view === "matching") {
        await page
          .getByRole("button", { name: "Analyze this match", exact: true })
          .click();
        await expect(page.locator(".gps .projected-score")).toHaveText(/\d/);
      }
      const reading = await page.evaluate(async () => {
        await document.fonts.ready;
        const nodes = document.createTreeWalker(
          document.body,
          NodeFilter.SHOW_TEXT,
        );
        const tiny: { text: string; size: number }[] = [];
        while (nodes.nextNode()) {
          const node = nodes.currentNode,
            element = node.parentElement;
          if (
            !element ||
            !node.textContent?.trim() ||
            element.closest("svg,script,style,option") ||
            !element.getBoundingClientRect().width ||
            !element.getBoundingClientRect().height
          )
            continue;
          const style = getComputedStyle(element);
          if (style.visibility !== "hidden" && parseFloat(style.fontSize) < 14)
            tiny.push({
              text: node.textContent.slice(0, 70),
              size: parseFloat(style.fontSize),
            });
        }
        return {
          tiny,
          width: innerWidth,
          scroll: document.documentElement.scrollWidth,
          fontLoaded: [...document.fonts].some(
            (face) => face.family.includes("Inter") && face.status === "loaded",
          ),
          bodySize: getComputedStyle(document.body).fontSize,
        };
      });
      expect(reading.tiny, `${view} at ${width}px`).toEqual([]);
      expect(
        reading.scroll,
        `${view} horizontal overflow at ${width}px`,
      ).toBeLessThanOrEqual(reading.width);
      expect(reading.fontLoaded).toBe(true);
      expect(reading.bodySize).toBe("16px");
    }
  }
  expect(externalFonts).toEqual([]);
});

test("200% text enlargement retains overview and module controls", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 1000 });
  for (const view of [
    "overview",
    "jd",
    "resume",
    "profile",
    "talent",
    "matching",
  ]) {
    await page.goto(`/#${view}`);
    await page.addStyleTag({ content: ":root { font-size: 200%; }" });
    await expect(
      page.getByRole("heading", { level: 1 }).filter({ visible: true }),
    ).toBeVisible();
    const size = await page.evaluate(() => ({
      body: getComputedStyle(document.body).fontSize,
      scroll: document.documentElement.scrollWidth,
      width: innerWidth,
    }));
    expect(size.body).toBe("32px");
    expect(
      size.scroll,
      `text enlargement overflow in ${view}`,
    ).toBeLessThanOrEqual(size.width);
    await expect(
      page.getByRole("combobox", { name: "Selected candidate" }),
    ).toBeVisible();
    await expect(
      page.getByRole("combobox", { name: "Selected job" }),
    ).toBeVisible();
  }
});
