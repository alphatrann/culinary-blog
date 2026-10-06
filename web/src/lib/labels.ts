export type DifficultyName = "easy" | "medium" | "hard" | "expert";
export type RecipeStatusName = "draft" | "published" | "archived";

export const difficultyLabels: Record<DifficultyName, string> = {
  easy: "Dễ",
  medium: "Trung bình",
  hard: "Khó",
  expert: "Rất khó",
};

export const recipeStatusLabels: Record<RecipeStatusName, string> = {
  draft: "Bản nháp",
  published: "Đã đăng",
  archived: "Đã lưu trữ",
};

// The API serialises the IntEnums as numbers but accepts names in query params; support both.
const difficultyByValue: DifficultyName[] = ["easy", "medium", "hard", "expert"];
const statusByValue: RecipeStatusName[] = ["draft", "published", "archived"];

export function difficultyLabel(value: DifficultyName | number): string {
  const name = typeof value === "number" ? difficultyByValue[value - 1] : value;
  return difficultyLabels[name] ?? "";
}

export function recipeStatusLabel(value: RecipeStatusName | number): string {
  const name = typeof value === "number" ? statusByValue[value] : value;
  return recipeStatusLabels[name] ?? "";
}

/** 45 → "45 phút", 180 → "3 giờ", 90 → "1 giờ 30 phút". */
export function formatMinutes(minutes: number): string {
  const total = Math.max(0, Math.round(minutes));
  const h = Math.floor(total / 60);
  const m = total % 60;
  if (h === 0) return `${m} phút`;
  return m === 0 ? `${h} giờ` : `${h} giờ ${m} phút`;
}
