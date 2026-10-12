export const LOGIN_PATH = "/auth/login";

/** Accept only same-origin relative paths so `?next=` can't become an open redirect. */
export function safeNext(raw: string | null | undefined): string | null {
  if (!raw || !raw.startsWith("/") || raw.startsWith("//") || /[\\\u0000-\u001f]/.test(raw)) {
    return null;
  }
  return raw;
}

export function loginUrl(next: string): string {
  const safe = safeNext(next);
  return safe && safe !== "/" ? `${LOGIN_PATH}?next=${encodeURIComponent(safe)}` : LOGIN_PATH;
}
