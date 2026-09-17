# ADR-0006: Rate limiting algorithm per endpoint class

## Status

Accepted

## Context

- NFR-SEC-003 requires per-IP rate limiting on auth, general API, and upload endpoints, state held in Redis.
- The three endpoint classes have different traffic shapes: auth is a brute-force/credential-stuffing target; general reads (recipe/category browsing) are legitimately bursty; uploads are a target for IP-rotation abuse.

## Decision

- **Auth (`/auth/*`):** sliding window counter. `limit=10`, `windowSize=60s`, key `TTL=90s` (matches SRS NFR-SEC-003). Chosen over a sliding window log for lower memory (one counter per window, not a timestamp per request), accepting boundary inaccuracy near window edges.
- **General API (recipe/category reads):** token bucket, 100 tokens/min/IP, continuous refill — allows legitimate bursts (e.g. rapidly paging through recipes) instead of hard-clipping at a fixed window boundary.
- **Upload (`/recipes/{id}/images`):** sliding window counter, `limit=5`, `windowSize=60s`, `TTL=90s`, enforced on **both** a per-IP key and a per-user_id key (request must pass both) — closes the gap where IP rotation bypasses a per-IP-only limit.

## Consequences

- Three algorithms for three endpoint classes is more moving parts than one blanket limiter, but each pick matches a distinct threat/traffic shape rather than being applied uniformly by default.
- Sliding window counter's boundary inaccuracy (up to ~2x the limit can pass across a window boundary) is an accepted tradeoff for memory — acceptable on auth because it isn't the only brute-force guard (account lockout after 5 failed attempts, FR-AUTH-002, still applies).
- Token bucket's generous burst absorption is fine for cache-backed public reads (ADR-0003); don't reuse it for a write endpoint without reconsidering.
- Per-IP + per-user_id double enforcement on upload costs one extra Redis check per request but is the only one of the three limiters actually designed against a rotating-identity attacker.
- At `limit=10`/`windowSize=60s`, the sliding window counter's boundary inaccuracy can let up to ~20 requests through across a window edge — still a meaningful throttle relative to account lockout (5 failed attempts, FR-AUTH-002), but worth knowing the actual worst case isn't a hard 10/min.
