// Shared helpers for the k6 scripts (NFR-PERF-001/002). Run: k6 run -e BASE_URL=http://localhost:8000 smoke.js
import http from "k6/http";
import { check } from "k6";

export const BASE = __ENV.BASE_URL || "http://localhost:8000";
const API = `${BASE}/api/v1`;
const SEARCH_TERMS = ["pho", "bun", "ga", "com", "banh mi", "canh chua", "thit kho", "goi cuon", "che", "xoi"];
const DIFFICULTIES = ["easy", "medium", "hard", "expert"]; // the API takes names, not ints
const SORTS = ["-created_at", "created_at", "title", "-title", "cook_time_minutes", "-cook_time_minutes"];

const __VU_LOGGED_IN = new Set();
const pick = (xs) => xs[Math.floor(Math.random() * xs.length)];

// Thresholds mirror NFR-PERF-001; per-endpoint so a slow endpoint can't hide behind fast ones.
export const ENDPOINTS = ["login", "list_recipes_auth", "list_recipes", "recipe_detail", "categories", "category_detail", "search", "me"];
export function thresholds() {
  const t = { http_req_failed: ["rate<0.01"] };
  for (const name of ENDPOINTS) {
    t[`http_req_duration{endpoint:${name}}`] = ["p(50)<150", "p(95)<500", "p(99)<1000"];
  }
  return t;
}

// Discovers real ids/slugs so the run works against any dataset size.
export function setup() {
  const categories = http.get(`${API}/categories`).json();
  const slugs = [];
  for (let page = 1; page <= 5 && slugs.length < 200; page++) {
    const body = http.get(`${API}/recipes?page=${page}&page_size=50`).json();
    for (const r of body.items) slugs.push(r.slug);
  }
  const email = __ENV.LOGIN_EMAIL || "seed.author@example.com";
  const password = __ENV.LOGIN_PASSWORD || "SeedAuthor#2026";
  return { categories: categories.map((c) => ({ id: c.id, slug: c.slug })), slugs, email, password };
}

const get = (url, endpoint) => {
  const res = http.get(url, { tags: { endpoint, name: endpoint } });
  // `name` groups URLs: unique ids in URLs otherwise explode k6 metric series
  check(res, { [`${endpoint} 2xx`]: (r) => r.status >= 200 && r.status < 300 });
  return res;
};

function listParams(data) {
  const page = Math.random() < 0.8 ? 1 + Math.floor(Math.random() * 3) : 1 + Math.floor(Math.random() * 100);
  const params = [`page=${page}`, `sort=${pick(SORTS)}`];
  if (Math.random() < 0.5) params.push(`category_id=${pick(data.categories).id}`);
  if (Math.random() < 0.3) params.push(`difficulty=${pick(DIFFICULTIES)}`);
  if (Math.random() < 0.2) params.push(`max_cook_time=${15 + Math.floor(Math.random() * 60)}`);
  return params;
}

// Logs the VU in once (k6 keeps the cookie jar per VU with noCookiesReset).
function ensureLogin(data) {
  if (!__VU_LOGGED_IN.has(__VU)) {
    login(data);
    __VU_LOGGED_IN.add(__VU);
  }
}

// One weighted user action: guest list 25, non-admin list 10, detail 25, categories 10, category detail 10,
// search 15, me 5.
export function browse(data) {
  const roll = Math.random() * 100;
  if (roll < 25) {
    get(`${API}/recipes?${listParams(data).join("&")}`, "list_recipes");
  } else if (roll < 35) {
    // Non-admin viewer: visibility is `status = published OR author_id = me`, a different plan than the guest list.
    ensureLogin(data);
    get(`${API}/recipes?${listParams(data).join("&")}`, "list_recipes_auth");
  } else if (roll < 60) {
    get(`${API}/recipes/${pick(data.slugs)}`, "recipe_detail");
  } else if (roll < 70) {
    get(`${API}/categories`, "categories");
  } else if (roll < 80) {
    get(`${API}/categories/${pick(data.categories).slug}`, "category_detail");
  } else if (roll < 95) {
    const q = encodeURIComponent(pick(SEARCH_TERMS));
    const cat = Math.random() < 0.3 ? `&category_id=${pick(data.categories).id}` : "";
    get(`${API}/recipes/search?q=${q}${cat}`, "search");
  } else {
    ensureLogin(data);
    get(`${API}/auth/me`, "me");
  }
}

// Argon2 login is deliberately separate: SRS caps auth at 10 req/min/IP, so it is not part of the throughput mix.
export function login(data) {
  const res = http.post(`${API}/auth/login`, JSON.stringify({ email: data.email, password: data.password }), {
    headers: { "Content-Type": "application/json" },
    tags: { endpoint: "login" },
  });
  check(res, { "login 200": (r) => r.status === 200 });
}
