import { z } from "zod";
import type { RequestBody } from "@/lib/api";

/** Form values are kept as strings (raw inputs); `toCreatePayload` converts them for the API. */

const positiveInt = (label: string) =>
  z
    .string()
    .trim()
    .min(1, `Vui lòng nhập ${label}.`)
    .refine(
      (v) => /^\d+$/.test(v) && Number(v) > 0,
      `${label[0].toUpperCase()}${label.slice(1)} phải là số nguyên lớn hơn 0.`,
    );

const optionalDecimal = (label: string) =>
  z
    .string()
    .trim()
    .refine(
      (v) => v === "" || (/^\d{1,8}([.,]\d{1,2})?$/.test(v) && Number(v.replace(",", ".")) >= 0),
      `${label} phải là số không âm (tối đa 2 chữ số thập phân).`,
    );

export const ingredientSchema = z
  .object({
    /** Server id of an existing ingredient (edit mode); absent on rows that have not been saved yet. */
    id: z.string().optional(),
    name: z.string().trim().max(100, "Tối đa 100 ký tự."),
    quantity: z
      .string()
      .trim()
      .refine(
        (v) => v === "" || (/^\d{1,10}([.,]\d{1,3})?$/.test(v) && Number(v.replace(",", ".")) > 0),
        "Số lượng phải lớn hơn 0.",
      ),
    unit: z.string().trim().max(50, "Tối đa 50 ký tự."),
  })
  .superRefine((v, ctx) => {
    // Fully blank rows are allowed (dropped on submit); a partly filled row needs a name.
    if (!v.name && (v.quantity || v.unit)) {
      ctx.addIssue({ code: "custom", path: ["name"], message: "Nhập tên nguyên liệu." });
    }
    if (v.quantity && !v.unit) {
      ctx.addIssue({ code: "custom", path: ["unit"], message: "Nhập đơn vị." });
    } else if (v.unit && !v.quantity) {
      ctx.addIssue({ code: "custom", path: ["quantity"], message: "Nhập số lượng." });
    }
  });

export const stepSchema = z.object({
  /** Server id of an existing step (edit mode). */
  id: z.string().optional(),
  text: z.string().trim().max(2000, "Nội dung bước tối đa 2000 ký tự."),
});

export const recipeFormSchema = z.object({
  title: z
    .string()
    .trim()
    .min(5, "Tiêu đề cần từ 5 đến 200 ký tự.")
    .max(200, "Tiêu đề cần từ 5 đến 200 ký tự.")
    .refine((v) => !/[<>]/.test(v), "Tiêu đề không được chứa ký tự < hoặc >."),
  description: z.string().trim().min(1, "Vui lòng nhập mô tả."),
  category_id: z.string().min(1, "Vui lòng chọn danh mục."),
  difficulty: z.enum(["1", "2", "3", "4"], "Vui lòng chọn độ khó."),
  prep_time_minutes: positiveInt("thời gian chuẩn bị"),
  cook_time_minutes: positiveInt("thời gian nấu"),
  servings: positiveInt("khẩu phần"),
  ingredients: z.array(ingredientSchema),
  steps: z.array(stepSchema),
  nutrition: z.object({
    calories: optionalDecimal("Năng lượng"),
    protein: optionalDecimal("Đạm"),
    fat: optionalDecimal("Chất béo"),
    carbohydrates: optionalDecimal("Tinh bột"),
  }),
});

export type RecipeFormValues = z.infer<typeof recipeFormSchema>;
export type RecipeCreatePayload = RequestBody<"/recipes", "post">;

export const emptyRecipeForm: RecipeFormValues = {
  title: "",
  description: "",
  category_id: "",
  difficulty: "1",
  prep_time_minutes: "",
  cook_time_minutes: "",
  servings: "",
  ingredients: [{ name: "", quantity: "", unit: "" }],
  steps: [{ text: "" }],
  nutrition: { calories: "", protein: "", fat: "", carbohydrates: "" },
};

const STEP_TITLE_MAX = 200;

/** Steps are a single textarea in the UI; the API also wants a title, so use the first line. */
export function deriveStepTitle(text: string): string {
  const first = text.trim().split(/\r?\n/, 1)[0].trim();
  return first.length > STEP_TITLE_MAX ? `${first.slice(0, STEP_TITLE_MAX - 1).trimEnd()}…` : first;
}

const num = (v: string) => Number(v.trim().replace(",", "."));

export function isPublishable(values: Pick<RecipeFormValues, "ingredients" | "steps">) {
  return {
    ingredients: values.ingredients.some((i) => i.name.trim() !== ""),
    steps: values.steps.some((s) => s.text.trim() !== ""),
  };
}

export function toCreatePayload(values: RecipeFormValues): RecipeCreatePayload {
  const nutrition = Object.fromEntries(
    Object.entries(values.nutrition)
      .filter(([, v]) => v.trim() !== "")
      .map(([k, v]) => [k, num(v)]),
  );
  return {
    title: values.title.trim(),
    description: values.description.trim(),
    category_id: values.category_id,
    difficulty: Number(values.difficulty) as RecipeCreatePayload["difficulty"],
    prep_time_minutes: Number(values.prep_time_minutes),
    cook_time_minutes: Number(values.cook_time_minutes),
    servings: Number(values.servings),
    ingredients: values.ingredients
      .filter((i) => i.name.trim() !== "")
      .map((i, index) => ({
        name: i.name.trim(),
        quantity: i.quantity.trim() ? num(i.quantity) : null,
        unit: i.unit.trim() || null,
        order_index: index,
      })),
    steps: values.steps
      .filter((s) => s.text.trim() !== "")
      .map((s) => ({
        title: deriveStepTitle(s.text),
        description: s.text.trim(),
      })),
    nutrition: Object.keys(nutrition).length ? nutrition : null,
  };
}
