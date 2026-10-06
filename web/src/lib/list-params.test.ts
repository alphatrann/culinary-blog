import { describe, expect, it } from "vitest";
import { buildHref, listSortOptions, parseListParams } from "./list-params";

describe("parseListParams", () => {
  it("accepts valid values", () => {
    const id = "123e4567-e89b-12d3-a456-426614174000";
    expect(
      parseListParams({
        category_id: id,
        difficulty: "easy",
        max_cook_time: "30",
        sort: "title",
        page: "3",
      }),
    ).toEqual({ category_id: id, difficulty: "easy", max_cook_time: 30, sort: "title", page: 3 });
  });

  it("drops invalid values", () => {
    expect(
      parseListParams({
        category_id: "nope",
        difficulty: "x",
        max_cook_time: "-1",
        sort: "bad",
        page: "0",
      }),
    ).toEqual({
      category_id: undefined,
      difficulty: undefined,
      max_cook_time: undefined,
      sort: undefined,
      page: 1,
    });
  });
});

describe("buildHref", () => {
  it("omits empty values and page 1", () => {
    expect(buildHref("/recipes", { sort: "title", page: 1, difficulty: undefined })).toBe(
      "/recipes?sort=title",
    );
    expect(buildHref("/recipes", {})).toBe("/recipes");
  });
});

describe("listSortOptions", () => {
  it("offers newest, A–Z and quickest", () => {
    expect(listSortOptions.map((o) => o.value)).toEqual([
      "-created_at",
      "title",
      "cook_time_minutes",
    ]);
  });
});
