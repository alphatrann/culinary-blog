"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, Search, X } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { useSession } from "@/lib/session";
import { mainNav } from "./nav-links";
import { SearchForm } from "./search-form";

const iconBtn =
  "flex size-11 items-center justify-center rounded-md text-foreground hover:bg-accent";
const linkClass =
  "flex min-h-11 items-center rounded-md px-3 text-sm font-medium text-foreground hover:bg-accent";

/** Below `lg` the nav collapses here; below `md` search and auth actions do too. */
export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useSession();

  useEffect(() => setOpen(false), [pathname]);

  return (
    <>
      <Link href="/search" aria-label="Tìm kiếm" className={`${iconBtn} md:hidden`}>
        <Search className="size-5" aria-hidden="true" />
      </Link>
      <button
        type="button"
        className={`${iconBtn} lg:hidden`}
        aria-label={open ? "Đóng menu" : "Mở menu"}
        aria-expanded={open}
        aria-controls="mobile-menu"
        onClick={() => setOpen((o) => !o)}
      >
        {open ? (
          <X className="size-5" aria-hidden="true" />
        ) : (
          <Menu className="size-5" aria-hidden="true" />
        )}
      </button>
      {open && (
        <div
          id="mobile-menu"
          className="absolute inset-x-0 top-full z-40 flex flex-col gap-1 border-b border-border bg-background px-4 py-3 shadow-md lg:hidden"
        >
          <SearchForm id="hd-q-mobile" className="mb-2 md:hidden" />
          <nav aria-label="Điều hướng chính" className="flex flex-col">
            {mainNav.map((l) => (
              <Link key={l.href} href={l.href} className={linkClass}>
                {l.label}
              </Link>
            ))}
          </nav>
          <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3 md:hidden">
            {user ? (
              <>
                <Link href="/profile" className={linkClass}>
                  Hồ sơ
                </Link>
                <Link href="/my-recipes" className={linkClass}>
                  Công thức của tôi
                </Link>
                <button type="button" onClick={logout} className={`${linkClass} text-left`}>
                  Đăng xuất
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className={buttonVariants({ variant: "outline" })}>
                  Đăng nhập
                </Link>
                <Link href="/register" className={buttonVariants()}>
                  Đăng ký
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
