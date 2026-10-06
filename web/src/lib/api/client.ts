import { publicApiBaseUrl } from "@/lib/env";
import { apiErrorFromResponse, ApiError } from "./errors";
import { resolvePath } from "./url";
import type { ApiPaths, ParamOptions, PathsWith, RequestBody, ResponseBody } from "./types";

type Method = "get" | "post" | "put" | "patch" | "delete";

export interface RequestOptions {
  /** Sent as `If-Match` (optimistic concurrency on `row_version`). */
  rowVersion?: number | string;
  /** Passed through as `X-Correlation-ID`; generated when omitted. */
  correlationId?: string;
  signal?: AbortSignal;
  /** JSON body. Ignored when `formData` is set. */
  body?: unknown;
  /** Multipart body for uploads; the browser sets the boundary header. */
  formData?: FormData;
  path?: Record<string, string | number>;
  query?: Record<string, unknown>;
}

type Listener = () => void;

/**
 * Typed fetch wrapper for the browser. Cookies carry auth (`credentials: 'include'`, never an
 * `Authorization` header — SRS §5.2). A 401 triggers one single-flight `POST /auth/refresh` and a
 * retry; if refresh fails the signed-out listeners fire and the original 401 is thrown.
 */
export class ApiClient {
  private refreshInFlight: Promise<boolean> | null = null;
  private readonly signedOutListeners = new Set<Listener>();

  constructor(
    private readonly baseUrl: string = publicApiBaseUrl,
    private readonly fetchImpl: typeof fetch = (...args) => fetch(...args),
  ) {}

  /** Subscribe to "session expired and refresh failed". Returns an unsubscribe function. */
  onSignedOut(listener: Listener): () => void {
    this.signedOutListeners.add(listener);
    return () => this.signedOutListeners.delete(listener);
  }

  get<P extends PathsWith<"get">>(
    path: P,
    options?: Omit<RequestOptions, "body" | "formData" | "path" | "query"> & ParamOptions<P, "get">,
  ) {
    return this.request<ResponseBody<P, "get">>("get", path, options as RequestOptions);
  }

  post<P extends PathsWith<"post">>(
    path: P,
    options?: Omit<RequestOptions, "body" | "path" | "query"> &
      ParamOptions<P, "post"> & { body?: RequestBody<P, "post"> },
  ) {
    return this.request<ResponseBody<P, "post">>("post", path, options as RequestOptions);
  }

  put<P extends PathsWith<"put">>(
    path: P,
    options?: Omit<RequestOptions, "body" | "path" | "query"> &
      ParamOptions<P, "put"> & { body?: RequestBody<P, "put"> },
  ) {
    return this.request<ResponseBody<P, "put">>("put", path, options as RequestOptions);
  }

  patch<P extends PathsWith<"patch">>(
    path: P,
    options?: Omit<RequestOptions, "body" | "path" | "query"> &
      ParamOptions<P, "patch"> & { body?: RequestBody<P, "patch"> },
  ) {
    return this.request<ResponseBody<P, "patch">>("patch", path, options as RequestOptions);
  }

  delete<P extends PathsWith<"delete">>(
    path: P,
    options?: Omit<RequestOptions, "body" | "formData" | "path" | "query"> &
      ParamOptions<P, "delete">,
  ) {
    return this.request<ResponseBody<P, "delete">>("delete", path, options as RequestOptions);
  }

  private async request<T>(
    method: Method,
    path: keyof ApiPaths,
    options: RequestOptions = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${resolvePath(path as string, options)}`;
    let response = await this.send(method, url, options);

    if (response.status === 401 && !isAuthEndpoint(path as string)) {
      if (await this.refreshOnce()) {
        response = await this.send(method, url, options);
      } else {
        this.signedOutListeners.forEach((listener) => listener());
      }
    }

    if (!response.ok) throw await apiErrorFromResponse(response);
    if (response.status === 204 || response.status === 205) return undefined as T;
    return (await response.json()) as T;
  }

  private send(method: Method, url: string, options: RequestOptions): Promise<Response> {
    const headers = new Headers({
      Accept: "application/json",
      "X-Correlation-ID": options.correlationId ?? crypto.randomUUID(),
    });
    let body: BodyInit | undefined;
    if (options.formData) {
      body = options.formData;
    } else if (options.body !== undefined) {
      headers.set("Content-Type", "application/json");
      body = JSON.stringify(options.body);
    }
    if (options.rowVersion !== undefined) headers.set("If-Match", String(options.rowVersion));

    return this.fetchImpl(url, {
      method: method.toUpperCase(),
      headers,
      body,
      credentials: "include",
      signal: options.signal,
    });
  }

  /** Concurrent 401s share one refresh call (the server rotates the token, so a second call would trip reuse detection). */
  private refreshOnce(): Promise<boolean> {
    this.refreshInFlight ??= this.send("post", `${this.baseUrl}/auth/refresh`, {})
      .then((response) => response.ok)
      .catch(() => false)
      .finally(() => {
        this.refreshInFlight = null;
      });
    return this.refreshInFlight;
  }
}

/** Auth endpoints answer 401 for bad credentials/tokens; refreshing on them would loop or mask the error. */
function isAuthEndpoint(path: string): boolean {
  return ["/auth/login", "/auth/register", "/auth/refresh"].includes(path);
}

export { ApiError };

/** Shared browser instance. */
export const api = new ApiClient();
