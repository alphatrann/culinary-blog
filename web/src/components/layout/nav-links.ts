export const mainNav = [
  { href: "/recipes", label: "Công thức" },
  { href: "/categories", label: "Danh mục" },
  { href: "/dashboard/recipes/new", label: "Viết công thức" },
] as const;

const HEAVY_PREFIXES = ["/dashboard", "/auth", "/profile"];

/**
 * Next prefetches the JS of every `<Link>` in the viewport. The editor and dashboard routes are 160-240 kB each and
 * sit in the header and footer of every page, so prefetching them put ~100 kB of script on a first visit to `/` and
 * broke the Lighthouse script budget (NFR-PERF-005). Hover and focus still prefetch them; only the eager one is off.
 */
export function prefetchFor(href: string): false | undefined {
  return HEAVY_PREFIXES.some((p) => href === p || href.startsWith(`${p}/`)) ? false : undefined;
}
