import type { FieldPath } from "react-hook-form";
import { isApiError } from "@/lib/api";
import { IMAGE_FORMAT_ERROR } from "./images";
import type { RecipeFormValues } from "./schemas";

export interface RecipeFailure {
  banner?: string;
  fields: Partial<Record<string, string>>;
}

const GENERIC = "Đã có lỗi xảy ra. Vui lòng thử lại.";

/** Maps API `steps.N.title|description` / `ingredients.N.*` paths back onto form field names. */
function toFormPath(path: string): string {
  return path.replace(/^steps\.(\d+)\.(title|description)$/, "steps.$1.text");
}

/** Maps a create/publish failure onto a banner and/or per-field messages. */
export function mapRecipeError(error: unknown): RecipeFailure {
  if (!isApiError(error)) return { banner: GENERIC, fields: {} };
  if (error.status === 401) {
    return { banner: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", fields: {} };
  }
  if (error.status === 403) {
    return { banner: "Bạn không có quyền tạo công thức.", fields: {} };
  }
  if (error.isRateLimited) {
    return { banner: "Bạn thao tác quá nhanh. Vui lòng thử lại sau ít phút.", fields: {} };
  }
  if (error.status === 422) {
    const fields: RecipeFailure["fields"] = {};
    for (const [path, message] of Object.entries(error.errors)) fields[toFormPath(path)] = message;
    if (Object.keys(fields).length) return { fields };
    return { banner: error.detail || GENERIC, fields };
  }
  return { banner: GENERIC, fields: {} };
}

/** Maps an image upload, primary or delete failure onto one Vietnamese message. */
export function mapImageError(error: unknown): string {
  if (!isApiError(error)) return GENERIC;
  if (error.status === 400) return error.detail || IMAGE_FORMAT_ERROR;
  if (error.status === 413) return "Ảnh vượt quá dung lượng tối đa 5 MB.";
  if (error.status === 401) return "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
  if (error.status === 403) return "Bạn không có quyền chỉnh sửa ảnh của công thức này.";
  if (error.isRateLimited) return "Bạn tải ảnh quá nhanh. Vui lòng thử lại sau ít phút.";
  return GENERIC;
}

export type RecipeFieldPath = FieldPath<RecipeFormValues>;

export const PUBLISH_INCOMPLETE = "Cần ít nhất 1 nguyên liệu và 1 bước thực hiện để xuất bản.";
