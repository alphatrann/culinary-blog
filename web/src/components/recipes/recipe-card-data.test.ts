import { describe, expect, it } from "vitest";
import { toRecipeCardData, type RecipeSummary } from "./recipe-card-data";

const summary = {
  slug: "pho-bo",
  title: "Phở bò",
  category_name: "Món nước",
  prep_time_minutes: 30,
  cook_time_minutes: 150,
  difficulty: 2,
  author_name: "Minh Anh",
  thumbnail_url: null,
} as unknown as RecipeSummary;

describe("toRecipeCardData", () => {
  it("sums prep and cook time and labels the difficulty in Vietnamese", () => {
    expect(toRecipeCardData(summary)).toMatchObject({
      slug: "pho-bo",
      category: "Món nước",
      time: "3 giờ",
      difficulty: "Trung bình",
      author: "Minh Anh",
      thumbnailUrl: null,
    });
  });
});
