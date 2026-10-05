# Mockups

Design reference for the M7 frontend (`web/`). These are exported Design Components, **not production code**: replicate the colors, type, spacing and layout in the Next.js components, don't copy the markup.

Open any `*.dc.html` in a browser (they link to each other relatively; `support.js` and `vendor/` render them). Language is Vietnamese.

| Screen | Desktop (1440) | Tablet (820) | Mobile (390) |
| --- | --- | --- | --- |
| Header (Thanh điều hướng) | `Header.dc.html` | | |
| Footer (Chân trang) | `Footer.dc.html` | | |
| Recipe card (Thẻ công thức) | `RecipeCard.dc.html` | | |
| Home (Trang chủ) | `Main.dc.html` | `HomeTablet.dc.html` | `HomeMobile.dc.html` |
| Recipe detail (Chi tiết công thức) | `Recipe.dc.html` | `RecipeTablet.dc.html` | `RecipeMobile.dc.html` |
| Login (Đăng nhập) | `Auth.dc.html` | `LoginTablet.dc.html` | `LoginMobile.dc.html` |
| Register (Đăng ký) | `RegisterDesktop.dc.html` | `RegisterTablet.dc.html` | `RegisterMobile.dc.html` |
| Search (Tìm kiếm) | `Search.dc.html` | `SearchTablet.dc.html` | `SearchMobile.dc.html`, `SearchMobileFilter.dc.html` (filter open) |
| Profile + my recipes (Hồ sơ cá nhân) | `Profile.dc.html` | `ProfileTablet.dc.html` | `ProfileMobile.dc.html` |
| Recipe editor (Viết công thức) | `Editor.dc.html` | `EditorTablet.dc.html` | `EditorMobile.dc.html` |

Not mocked: `/categories`, `/categories/[slug]`, `/dashboard` overview.
