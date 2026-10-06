import Link from "next/link";
import { Brand } from "./brand";
import { HeaderActions } from "./header-actions";
import { MobileMenu } from "./mobile-menu";
import { mainNav } from "./nav-links";
import { SearchForm } from "./search-form";

/** Server component: renders the guest state; auth-dependent parts hydrate client-side. */
export function SiteHeader() {
  return (
    <header className="relative border-b border-border bg-background print:hidden">
      <div className="mx-auto flex h-16 max-w-[1200px] items-center gap-1 pr-3 pl-4 md:gap-4 md:px-8">
        <Brand />
        <nav aria-label="Điều hướng chính" className="ml-4 hidden gap-1 lg:flex">
          {mainNav.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="flex h-11 items-center rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex-1" />
        <SearchForm id="hd-q" className="hidden w-[200px] lg:w-[260px] md:block" />
        <HeaderActions />
        <MobileMenu />
      </div>
    </header>
  );
}
