import type { RecipeDetail } from "./edit";

/** A saved recipe as `GET /recipes/{id}` returns it, for tests. Two steps and two ingredients, out of order on purpose. */
export const sampleRecipe = {
  id: "11111111-1111-4111-8111-111111111111",
  title: "Phở bò Hà Nội",
  slug: "pho-bo-ha-noi",
  description: "Món phở truyền thống.",
  prep_time_minutes: 30,
  cook_time_minutes: 180,
  servings: 4,
  difficulty: 2,
  status: 0,
  category_id: "22222222-2222-4222-8222-222222222222",
  category: { id: "22222222-2222-4222-8222-222222222222", name: "Món chính", slug: "mon-chinh" },
  author: { id: "33333333-3333-4333-8333-333333333333", display_name: "Chef", avatar_url: null },
  author_id: "33333333-3333-4333-8333-333333333333",
  published_at: null,
  created_at: "2026-10-01T00:00:00Z",
  row_version: 4,
  nutrition: { calories: 450, protein: null, fat: 9.5, carbohydrates: null },
  steps: [
    // Steps follow the editor's rule: the title is the first line of the description.
    {
      id: "s2",
      step_number: 2,
      title: "Ăn khi nóng.",
      description: "Ăn khi nóng.",
      duration_minutes: null,
      image_url: null,
    },
    {
      id: "s1",
      step_number: 1,
      title: "Ninh xương",
      description: "Ninh xương\nNinh xương 3 giờ.",
      duration_minutes: null,
      image_url: null,
    },
  ],
  ingredients: [
    { id: "i2", name: "Bánh phở", quantity: 500, unit: "g", notes: null, order_index: 1 },
    { id: "i1", name: "Thịt bò", quantity: null, unit: null, notes: null, order_index: 0 },
  ],
  images: [],
} as unknown as RecipeDetail;
