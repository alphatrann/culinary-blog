/** One entry of FastAPI's validation `errors` array (see `problem_details.py`). */
export interface ProblemFieldError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

/** Stable machine-readable codes the API sends in the `code` problem member (SRS Appendix B). */
export const ERROR_CODES = [
  "AUTH_EMAIL_EXISTS",
  "AUTH_INVALID_CREDENTIALS",
  "AUTH_TOKEN_EXPIRED",
  "AUTH_TOKEN_INVALID",
  "AUTH_REFRESH_TOKEN_EXPIRED",
  "AUTH_REFRESH_TOKEN_REVOKED",
  "AUTH_GOOGLE_TOKEN_INVALID",
  "AUTH_ACCOUNT_LOCKED",
  "RECIPE_NOT_FOUND",
  "RECIPE_PUBLISH_INCOMPLETE",
  "RECIPE_FORBIDDEN",
  "RECIPE_CONCURRENCY_CONFLICT",
  "INGREDIENT_QUANTITY_UNIT_MISMATCH",
  "CATEGORY_NOT_FOUND",
  "CATEGORY_NAME_EXISTS",
  "CATEGORY_DELETE_HAS_RECIPES",
  "FILE_SIZE_EXCEEDED",
  "FILE_MIME_INVALID",
  "VALIDATION_ERROR",
  "RATE_LIMIT_EXCEEDED",
] as const;

export type ErrorCode = (typeof ERROR_CODES)[number];

function toErrorCode(value: unknown): ErrorCode | undefined {
  return typeof value === "string" && (ERROR_CODES as readonly string[]).includes(value)
    ? (value as ErrorCode)
    : undefined;
}

/** RFC 7807 body as emitted by the API. */
export interface ProblemDetails {
  type?: string;
  title?: string;
  status?: number;
  detail?: string;
  instance?: string;
  /** Stable code (SRS Appendix B); absent for errors that have none. */
  code?: string;
  errors?: ProblemFieldError[];
}

/** Error thrown for every non-2xx API response. */
export class ApiError extends Error {
  readonly status: number;
  readonly title: string;
  readonly detail: string;
  readonly instance?: string;
  /** Machine-readable code; prefer it over `status` when the API sends one. Unknown codes read as undefined. */
  readonly code?: ErrorCode;
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
    this.code = toErrorCode(problem.code);
    this.errors = fieldErrors(problem.errors);
    this.correlationId = correlationId;
  }

  /** True when the API sent exactly this code. */
  is(code: ErrorCode): boolean {
    return this.code === code;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  /** Account temporarily locked after repeated failed logins. */
  get isLocked(): boolean {
    return this.is("AUTH_ACCOUNT_LOCKED") || (this.code === undefined && this.status === 423);
  }

  get isRateLimited(): boolean {
    return this.is("RATE_LIMIT_EXCEEDED") || (this.code === undefined && this.status === 429);
  }

  /** `If-Match` row_version mismatch (optimistic concurrency). */
  get isConflict(): boolean {
    return (
      this.is("RECIPE_CONCURRENCY_CONFLICT") ||
      (this.code === undefined && (this.status === 409 || this.status === 412))
    );
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
