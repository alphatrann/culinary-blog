# ADR-0015: Content-Security-Policy and security headers at nginx

## Status

Accepted

## Context

- NFR-SEC-004 asks for a `Content-Security-Policy` header as XSS defence. NFR-SEC-005 also asks for HSTS, but HSTS belongs with the HTTPS/TLS work, which is out of scope here.
- Next.js (App Router) emits inline bootstrap scripts and styles for hydration. A nonce-based CSP needs a middleware that makes each page dynamic, which would drop the ISR pages (`/categories`, `/categories/[slug]`, recipe detail) that NFR-PERF-003 relies on.
- `/docs` (FastAPI Swagger UI) loads its JavaScript and CSS from a CDN, so a strict CSP on the API location would break it.
- Recipe images come from object storage, and profile avatars (`avatar_url`) can point at any HTTPS host, so `img-src` cannot be limited to one origin.

## Decision

- nginx sends a CSP only on the web location (`/`), which serves the HTML pages. The policy allows `'self'` plus `'unsafe-inline'` for scripts and styles, and Google Identity Services at `accounts.google.com` (script, frame, connect). It allows images from `'self'`, `data:`, `blob:` and any `https:` origin. It sets `object-src 'none'`, `base-uri 'self'`, `form-action 'self'` and `frame-ancestors 'none'`.
- `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` and `X-Frame-Options: DENY` go on both the API and web locations.
- The API and `/docs` get no CSP. API responses are JSON, and the docs page needs its CDN.
- Headers use `always`, so error responses carry them too.

## Consequences

- `'unsafe-inline'` scripts weaken the CSP: an injected inline script would still run. The main protection is React's default escaping plus the rule that user HTML is never rendered. Upgrade path: nonces through a middleware, or hashes, once the ISR pages are reconsidered.
- `img-src https:` is broad. It is needed because avatars can come from any host. Narrowing it means restricting `avatar_url` to an allow-list, which would be a product decision.
- The headers exist only behind nginx. Local `next dev` on :3000 does not get them, so CSP violations appear in production first. Check the policy in a browser console when adding a new third-party script.
- HSTS and TLS redirects (NFR-SEC-005) are still open.
