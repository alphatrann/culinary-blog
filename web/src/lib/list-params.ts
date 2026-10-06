import type { DifficultyName } from "@/lib/labels";

export const sortOptions = [
  { value: "-created_at", label: "Mới nhất" },
  { value: "created_at", label: "Cũ nhất" },
  { value: "title", label: "Tên A–Z" },
  { value: "-title", label: "Tên Z–A" },
  { value: "cook_time_minutes", label: "Nấu nhanh nhất" },
  { value: "-cook_time_minutes", label: "Nấu lâu nhất" },
] as const;

/** Sort choices offered on the recipe list page (newest, A–Z, quickest). */
export const listSortOptions = sortOptions.filter((o) =>
  ["-created_at", "title", "cook_time_minutes"].includes(o.value),
);

export type SortValue = (typeof sortOptions)[number]["value"];

export const cookTimeOptions = [15, 30, 60, 120] as const;

export type ListSearchParams = Record<string, string | string[] | undefined>;

const difficulties: DifficultyName[] = ["easy", "medium", "hard", "expert"];

function first(v: string | string[] | undefined): string | undefined {
  return Array.isArray(v) ? v[0] : v;
}

const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Parse + sanitise URL params so invalid values never reach the API. */
export function parseListParams(sp: ListSearchParams) {
  const difficulty = first(sp.difficulty) as DifficultyName | undefined;
  const maxCook = Number(first(sp.max_cook_time));
  const sort = sortOptions.find((o) => o.value === first(sp.sort))?.value;
  const page = Number(first(sp.page));
  const categoryId = first(sp.category_id);
  return {
    page: Number.isInteger(page) && page >= 1 ? page : 1,
    difficulty: difficulty && difficulties.includes(difficulty) ? difficulty : undefined,
    max_cook_time: Number.isInteger(maxCook) && maxCook > 0 ? maxCook : undefined,
    category_id: categoryId && uuidPattern.test(categoryId) ? categoryId : undefined,
    sort,
  };
}

/** Build `?a=b&page=n` for the current path, dropping empty values. Resets nothing: callers pass the full set. */
export function buildHref(
  basePath: string,
  params: Record<string, string | number | undefined>,
): string {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "" && !(k === "page" && v === 1)) qs.set(k, String(v));
  }
  const s = qs.toString();
  return s ? `${basePath}?${s}` : basePath;
}
