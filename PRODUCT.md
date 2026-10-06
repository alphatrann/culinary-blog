# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Primary: home cooks, mostly anonymous Vietnamese-speaking readers on phone or laptop, browsing for a recipe to cook. Guests are the highest-priority audience (SRS 2.3). Secondary: Authors, registered users who publish and manage their own recipes; Admins, a small group who manage categories.

## Product Purpose
Culinary Blog is a recipe-sharing platform where Authors publish recipes with images, ingredients, steps, timings, difficulty and nutrition, and readers browse, filter and search them. Success is a reader finding a cookable recipe quickly and an Author getting a recipe published without friction.

## Positioning
Vietnamese-first discovery: diacritic-insensitive Vietnamese full-text search (PostgreSQL tsvector + unaccent) over community recipes with structured ingredients, steps, time and difficulty, organised by category.

## Operating Context
Public site served via nginx: Next.js for pages, FastAPI for `/api/v1`. Auth is cookie-based (HttpOnly JWT). Recipe detail pages are SEO-sensitive (Open Graph, JSON-LD Recipe markup, ISR). Design reference mockups live in `mockups/` at desktop 1440, tablet 820 and mobile 390.

## Capabilities and Constraints
- All user-facing copy is Vietnamese with full diacritics.
- Out of scope for v1 (do not design UI implying them): comments, ratings, bookmarks/favourites, real-time notifications, direct messaging, e-commerce, native apps.
- Recipe images arrive asynchronously (thumbnail worker), so cards must handle a missing thumbnail.
- The frontend must build and render sensibly with no live API.
- Stack is fixed: Next.js 15 App Router, TypeScript strict, Tailwind v4, shadcn/ui (see CLAUDE.md).

## Evidence on Hand
Real content is limited to seeded recipes and images (`scripts/seed/`) and the mockups. There are no testimonials, user counts, press, chef profiles or benchmarks; do not fabricate any.

## Product Principles
- Findability first: search, filters and categories get the shortest path from arrival to a recipe.
- Vietnamese is the product language, not a translation layer.
- Honest content: show only real recipes, authors and numbers.
- Guest-first: the reading experience works fully without an account; authoring is an opt-in step up.
- Every screen handles loading, empty and error states.

## Accessibility & Inclusion
WCAG 2.1 AA, keyboard-operable, visible focus, responsive from 390px phone to 1440px desktop.
