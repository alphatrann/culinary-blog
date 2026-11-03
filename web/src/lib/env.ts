/** Base URL for server-side API calls (server components, route handlers). Read at request time, not build time. */
export function serverApiBaseUrl(): string {
  return process.env.API_BASE_URL ?? "http://localhost:8000";
}

/** Base URL for browser API calls. Same-origin by default so HttpOnly cookies work through nginx. */
export const publicApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

/** Public origin used for canonical URLs, Open Graph, and the sitemap reference in robots.txt. No trailing slash. */
export function siteUrl(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
}
