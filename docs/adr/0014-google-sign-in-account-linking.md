# ADR-0014: Google sign-in via client-side ID token and account linking

## Status

Accepted

## Context

- FR-AUTH-003 (S1) adds "Sign in with Google" next to email/password.
- The SRS already fixes the flow: Google Identity Services hands the browser an ID token, and the API verifies it. No backend redirect or callback route.
- A Google account and a password account can share an email. Linking them by email alone would let anyone who controls an unverified Google address take over the password account.

## Decision

- `POST /api/v1/auth/google` takes `{ "id_token" }`. The API verifies signature, `aud` (`GOOGLE_CLIENT_ID`), `iss` and `exp` with `google-auth`, and reads the claims.
- Lookup order is `google_sub`, then email. An email match is linked (`users.google_sub` is set) only when Google reports `email_verified`. An unverified email is rejected with 401.
- New Google users get role `author`, `email_confirmed = true` and no `password_hash`. Display name falls back to the email local part.
- Session cookies are the same as `/auth/login`. Locked and inactive accounts are refused.
- With `GOOGLE_CLIENT_ID` empty the endpoint answers 503. The web button renders only when `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is set.

## Consequences

- No new tables or migrations (`users.google_sub` already exists).
- Google certificates are fetched on each sign-in. Caching them is a follow-up if login latency matters.
- Two first-time sign-ins for the same account can race into a 409 instead of a retried lookup.
