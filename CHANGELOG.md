# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Frontend (M7, #22):** Next.js 15 app in `web/`: home, recipe list, recipe detail, categories, search, login and register, and the author area.
- **Recipe editor (#44, #46):** create a draft or publish in one page; edit an existing recipe at `/dashboard/recipes/[id]/edit`. Saves check the row version, and a conflicting save offers reload or overwrite. Publish, unpublish and delete are on the same page.
- **Image upload (#45):** drag-and-drop or file picker with per-file progress, set-primary and delete. Client-side checks match the server (JPEG, PNG, WebP or AVIF, up to 5 MB).
- **Author dashboard (#47):** `/dashboard/recipes` with status tabs and counts, `/dashboard` overview, and a profile page showing the author's recipes.
- **API: owner read by id (#46):** `GET /api/v1/recipes/{id}` returns a recipe, including drafts, to its owner or an admin, with an `ETag`.
- **API: author filter and status counts (#43):** `GET /api/v1/recipes?author_id=me|<id>&status=…` returns the author's recipes and per-status counts. Summaries include `updated_at` and `row_version`.
- **Accessibility (#48):** a skip-to-content link, reduced-motion support, and a fix for the serious contrast and naming issues found by axe.
- **End-to-end tests (#48):** Playwright specs for browsing, authoring and the skip link, with axe scans. Run with `npm run e2e` against a running stack.
- **CI (#49):** `web-e2e` runs the e2e suite against `compose.e2e.yml`. `lighthouse` enforces the budgets in `web/lighthouserc.json`.
- **Docs:** ADR-0014 (rendering per route, same-origin auth, performance budgets).

### Changed

- The recipe summary in list and search responses adds `updated_at` and `row_version` (additive).

### Fixed

- The category select on the edit page now shows the saved category.
- The header's "Công thức của tôi" link no longer leads to a missing page.
- Recipes cannot take the slug `new`, which is the create route; a recipe titled "New" gets `new-2`.
- nginx accepts 5 MB uploads (`client_max_body_size 6m`), where the 1 MB default returned 413.

[Unreleased]: https://github.com/alphatrann/culinary-blog/compare/main...HEAD
