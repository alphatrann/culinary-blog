import type { RequestOptions } from "./client";

/** Substitute `{param}` placeholders and append the query string; arrays become repeated keys. */
export function resolvePath(
  path: string,
  { path: pathParams, query }: Pick<RequestOptions, "path" | "query">,
): string {
  let resolved = path;
  for (const [key, value] of Object.entries(pathParams ?? {})) {
    resolved = resolved.replace(`{${key}}`, encodeURIComponent(String(value)));
  }
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value === undefined || value === null) continue;
    for (const item of Array.isArray(value) ? value : [value]) search.append(key, String(item));
  }
  const qs = search.toString();
  return qs ? `${resolved}?${qs}` : resolved;
}
