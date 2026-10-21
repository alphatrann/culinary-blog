import { buildHref, type ListSearchParams } from "@/lib/list-params";

/** Set to true once the archive feature ships (S3, #25). Until then archived recipes are not listed as a tab. */
export const SHOW_ARCHIVED = false;

export const MY_RECIPE_TABS = SHOW_ARCHIVED
  ? (["all", "published", "draft", "archived"] as const)
  : (["all", "published", "draft"] as const);

export type MyRecipeTab = (typeof MY_RECIPE_TABS)[number];

export const MY_RECIPES_PAGE_SIZE = 10;

const first = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

/** Reads `?status=` and `?page=`; anything unknown falls back to "all" / page 1. */
export function parseMyRecipesParams(sp: ListSearchParams): { tab: MyRecipeTab; page: number } {
  const raw = first(sp.status) ?? "";
  const tab = (MY_RECIPE_TABS as readonly string[]).includes(raw) ? (raw as MyRecipeTab) : "all";
  const page = Number(first(sp.page));
  return { tab, page: Number.isInteger(page) && page >= 1 ? page : 1 };
}

/** The API status filter for a tab; "all" sends no filter so the list includes every status. */
export function tabStatusFilter(tab: MyRecipeTab): "draft" | "published" | "archived" | undefined {
  return tab === "all" ? undefined : tab;
}

export function myRecipesHref(basePath: string, tab: MyRecipeTab, page: number): string {
  return buildHref(basePath, { status: tab === "all" ? undefined : tab, page });
}
