import { describe, expect, it } from "vitest";
import { toCardData } from "./to-card-data";

describe("toCardData", () => {
  it("sums prep and cook time and labels difficulty", () => {
    const card = toCardData({
      slug: "pho",
      title: "Phở bò",
      category_name: "Món nước",
      author_name: "An",
      thumbnail_url: null,
      prep_time_minutes: 30,
      cook_time_minutes: 60,
      difficulty: 2,
    });
    expect(card).toMatchObject({
      slug: "pho",
      time: "1 giờ 30 phút",
      difficulty: "Trung bình",
      author: "An",
    });
  });

  it("tolerates missing optional fields", () => {
    const card = toCardData({ slug: "a", title: "A", cook_time_minutes: 15, difficulty: "easy" });
    expect(card.category).toBeUndefined();
    expect(card.time).toBe("15 phút");
  });
});
