/** One entry of FastAPI's validation `errors` array (see `problem_details.py`). */
export interface ProblemFieldError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

/** RFC 7807 body as emitted by the API. */
export interface ProblemDetails {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  errors?: ProblemFieldError[];
}

/** Error thrown for every non-2xx API response. */
export class ApiError extends Error {
  readonly status: number;
  readonly title: string;
  readonly detail: string;
  readonly instance?: string;
  /** Field path (`body.title`, `body.steps.0.text` → without the `body`/`query` prefix) → first message. */
  readonly errors: Record<string, string>;
  readonly correlationId?: string;

  constructor(status: number, problem: ProblemDetails, correlationId?: string) {
    const title = problem.title ?? `HTTP ${status}`;
    super(problem.detail ?? title);
    this.name = "ApiError";
    this.status = status;
    this.title = title;
    this.detail = problem.detail ?? title;
    this.instance = problem.instance;
    this.errors = fieldErrors(problem.errors);
    this.correlationId = correlationId;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  /** `If-Match` row_version mismatch (optimistic concurrency). */
  get isConflict(): boolean {
    return this.status === 409 || this.status === 412;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

const LOCATION_PREFIXES = new Set(["body", "query", "path", "header", "cookie"]);

function fieldErrors(errors: ProblemFieldError[] | undefined): Record<string, string> {
  const map: Record<string, string> = {};
  for (const { loc, msg } of errors ?? []) {
    const parts = loc.length > 1 && LOCATION_PREFIXES.has(String(loc[0])) ? loc.slice(1) : loc;
    const key = parts.join(".");
    if (!(key in map)) map[key] = msg;
  }
  return map;
}

/** Build an ApiError from a failed Response; tolerates non-JSON bodies (proxy errors, etc.). */
export async function apiErrorFromResponse(response: Response): Promise<ApiError> {
  let problem: ProblemDetails = {};
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object") problem = body as ProblemDetails;
  } catch {
    problem = { title: response.statusText || undefined };
  }
  return new ApiError(
    response.status,
    problem,
    response.headers.get("X-Correlation-ID") ?? undefined,
  );
}
