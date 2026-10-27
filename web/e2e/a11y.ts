import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

/** Fails on any serious or critical WCAG 2.1 A/AA violation. Minor and moderate issues are reported in the PR, not here. */
export async function expectNoSeriousA11yViolations(page: Page, label: string): Promise<void> {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  const blocking = results.violations
    .filter((v) => v.impact === "serious" || v.impact === "critical")
    .map(
      (v) =>
        `${v.id} (${v.impact}): ${v.help} — ${v.nodes.length} node(s): ${v.nodes
          .map((n) => n.html.slice(0, 160))
          .join(" | ")}`,
    );
  expect(blocking, `${label}: serious/critical axe violations`).toEqual([]);
}
