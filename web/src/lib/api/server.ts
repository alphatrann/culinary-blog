import { serverApiBaseUrl } from "@/lib/env";
import { apiErrorFromResponse } from "./errors";
import { resolvePath } from "./url";
import type { ApiPaths, ParamOptions, PathsWith, ResponseBody } from "./types";

type ServerGetOptions<P extends PathsWith<"get">> = ParamOptions<P, "get"> & {
  /** ISR window in seconds; `false` for fully dynamic. Defaults to 60. */
  revalidate?: number | false;
  tags?: string[];
  correlationId?: string;
};

/**
 * GET helper for server components (SSR/ISR). Deliberately sends no cookies and never reads
 * `cookies()`/`headers()`, so anonymous pages stay statically cacheable. Authenticated data is
 * fetched in the browser via `api`.
 */
export async function serverGet<P extends PathsWith<"get">>(
  path: P,
  options?: ServerGetOptions<P>,
): Promise<ResponseBody<P, "get">> {
  const {
    path: pathParams,
    query,
    revalidate = 60,
    tags,
    correlationId,
  } = (options ?? {}) as {
    path?: Record<string, string | number>;
    query?: Record<string, unknown>;
    revalidate?: number | false;
    tags?: string[];
    correlationId?: string;
  };

  const headers: Record<string, string> = { Accept: "application/json" };
  if (correlationId) headers["X-Correlation-ID"] = correlationId;

  const response = await fetch(
    `${serverApiBaseUrl()}/api/v1${resolvePath(path, { path: pathParams, query })}`,
    {
      headers,
      credentials: "omit",
      next: { revalidate, tags },
    },
  );
  if (!response.ok) throw await apiErrorFromResponse(response);
  return (await response.json()) as ResponseBody<P, "get">;
}

export type { ApiPaths };
