import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "cn";

const item =
  "inline-flex h-11 min-w-11 items-center justify-center gap-1 rounded-md border border-transparent px-3 text-sm font-medium";

function pageList(page: number, count: number): (number | "gap")[] {
  const pages = new Set([1, count, page - 1, page, page + 1]);
  const sorted = [...pages].filter((p) => p >= 1 && p <= count).sort((a, b) => a - b);
  return sorted.flatMap((p, i) => (i > 0 && p - sorted[i - 1] > 1 ? ["gap" as const, p] : [p]));
}

/** Link-based pager (SSR/SEO friendly). `hrefFor` builds the URL for a page number. */
function Pagination({
  page,
  pageCount,
  hrefFor,
  className,
}: {
  page: number;
  pageCount: number;
  hrefFor: (page: number) => string;
  className?: string;
}) {
  if (pageCount <= 1) return null;
  const off = "pointer-events-none text-muted-foreground opacity-60";
  return (
    <nav
      aria-label="Phân trang"
      className={cn("flex items-center justify-center gap-1", className)}
    >
      {page > 1 ? (
        <Link href={hrefFor(page - 1)} className={cn(item, "hover:bg-accent")} rel="prev">
          <ChevronLeft aria-hidden className="size-4" /> Trước
        </Link>
      ) : (
        <span aria-disabled className={cn(item, off)}>
          <ChevronLeft aria-hidden className="size-4" /> Trước
        </span>
      )}
      {pageList(page, pageCount).map((p, i) =>
        p === "gap" ? (
          <span key={`gap-${i}`} aria-hidden className={cn(item, "text-muted-foreground")}>
            …
          </span>
        ) : (
          <Link
            key={p}
            href={hrefFor(p)}
            aria-current={p === page ? "page" : undefined}
            className={cn(
              item,
              p === page ? "border-herb bg-herb text-herb-foreground" : "hover:bg-accent",
            )}
          >
            {p}
          </Link>
        ),
      )}
      {page < pageCount ? (
        <Link href={hrefFor(page + 1)} className={cn(item, "hover:bg-accent")} rel="next">
          Sau <ChevronRight aria-hidden className="size-4" />
        </Link>
      ) : (
        <span aria-disabled className={cn(item, off)}>
          Sau <ChevronRight aria-hidden className="size-4" />
        </span>
      )}
    </nav>
  );
}

export { Pagination };
