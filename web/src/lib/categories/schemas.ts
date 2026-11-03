import { z } from "zod";

// Mirrors CategoryWrite in the API (FR-CAT-003/004): name 2–50 chars, no HTML.
export const categoryFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, "Tên danh mục cần từ 2 đến 50 ký tự.")
    .max(50, "Tên danh mục cần từ 2 đến 50 ký tự.")
    .refine((value) => !/[<>]/.test(value), "Tên danh mục không được chứa thẻ HTML."),
  description: z.string().max(2000, "Mô tả tối đa 2000 ký tự."),
  image_url: z
    .string()
    .max(500, "Liên kết ảnh tối đa 500 ký tự.")
    .refine(
      (value) => value === "" || /^https?:\/\//.test(value),
      "Liên kết ảnh phải bắt đầu bằng http:// hoặc https://.",
    ),
});

export type CategoryFormValues = z.infer<typeof categoryFormSchema>;

export const emptyCategoryForm: CategoryFormValues = { name: "", description: "", image_url: "" };

/** Empty optional fields are sent as null so an edit clears them (the PUT replaces the whole row). */
export function toCategoryPayload({ name, description, image_url }: CategoryFormValues) {
  return { name, description: description || null, image_url: image_url || null };
}
