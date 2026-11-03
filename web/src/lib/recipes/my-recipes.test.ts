import { describe, expect, it } from "vitest";
import { MY_RECIPE_TABS, myRecipesHref, parseMyRecipesParams, tabStatusFilter } from "./my-recipes";

describe("parseMyRecipesParams", () => {
  it("defaults to all recipes on page 1", () => {
    expect(parseMyRecipesParams({})).toEqual({ tab: "all", page: 1 });
  });

  it("accepts a known tab and page", () => {
    expect(parseMyRecipesParams({ status: "draft", page: "3" })).toEqual({ tab: "draft", page: 3 });
  });

  it("falls back for unknown tabs, including the hidden archived tab", () => {
    expect(parseMyRecipesParams({ status: "archived" }).tab).toBe("all");
    expect(parseMyRecipesParams({ status: "nope" }).tab).toBe("all");
  });

  it("rejects non-positive or non-integer pages", () => {
    expect(parseMyRecipesParams({ page: "0" }).page).toBe(1);
    expect(parseMyRecipesParams({ page: "2.5" }).page).toBe(1);
    expect(parseMyRecipesParams({ page: "abc" }).page).toBe(1);
  });

  it("uses the first value when a param is repeated", () => {
    expect(parseMyRecipesParams({ status: ["published", "draft"] }).tab).toBe("published");
  });
});

describe("tab helpers", () => {
  it("does not offer the archived tab until S3 ships", () => {
    expect(MY_RECIPE_TABS).toEqual(["all", "published", "draft"]);
  });

  it("sends no status filter for the all tab", () => {
    expect(tabStatusFilter("all")).toBeUndefined();
    expect(tabStatusFilter("draft")).toBe("draft");
  });

  it("builds links that keep the tab and drop page 1", () => {
    expect(myRecipesHref("/dashboard/recipes", "all", 1)).toBe("/dashboard/recipes");
    expect(myRecipesHref("/dashboard/recipes", "draft", 1)).toBe("/dashboard/recipes?status=draft");
    expect(myRecipesHref("/profile", "published", 2)).toBe("/profile?status=published&page=2");
  });
});
