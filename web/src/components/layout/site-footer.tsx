import Link from "next/link";
import { Brand, BRAND_NAME } from "./brand";

const columns = [
  {
    title: "Khám phá",
    links: [
      { href: "/recipes", label: "Công thức mới" },
      { href: "/categories", label: "Danh mục" },
      { href: "/search", label: "Tìm kiếm" },
    ],
  },
  {
    title: "Tài khoản",
    links: [
      { href: "/login", label: "Đăng nhập" },
      { href: "/register", label: "Đăng ký" },
      { href: "/recipes/new", label: "Viết công thức" },
    ],
  },
  {
    // Stub pages: not built yet.
    title: "Thông tin",
    links: [
      { href: "/about", label: "Giới thiệu" },
      { href: "/contact", label: "Liên hệ" },
      { href: "/terms", label: "Điều khoản sử dụng" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-background text-muted-foreground print:hidden">
      <div className="mx-auto grid max-w-[1200px] grid-cols-2 gap-x-6 gap-y-4 px-4 pt-8 pb-4 lg:grid-cols-[2fr_1fr_1fr_1fr] md:grid-cols-3 md:gap-10 md:px-8 md:pt-12 md:pb-8">
        <div className="col-span-full lg:col-span-1">
          <Brand asLink={false} />
          <p className="mt-3 max-w-80 text-sm leading-relaxed">
            Công thức nấu ăn Việt, từng bước rõ ràng cho bữa cơm gia đình.
          </p>
        </div>
        {columns.map((col) => (
          <nav key={col.title} aria-label={col.title}>
            <h2 className="mb-2 text-sm font-semibold text-foreground">{col.title}</h2>
            <ul>
              {col.links.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="flex min-h-11 items-center text-sm hover:text-foreground hover:underline"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}
      </div>
      <div className="mx-auto max-w-[1200px] border-t border-border px-4 pt-5 pb-7 text-sm md:px-8">
        © 2026 {BRAND_NAME}. Mọi quyền được bảo lưu.
      </div>
    </footer>
  );
}
