import Link from "next/link";
import { ChevronRight } from "lucide-react";

export type Crumb = { label: string; href?: string };

/** Last crumb (no `href`) is the current page. */
function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="pt-4 pb-2">
      <ol className="flex flex-wrap items-center gap-x-1.5 text-muted-foreground">
        {items.map((item, i) => (
          <li key={item.label} className="inline-flex min-h-11 items-center gap-1.5">
            {item.href ? (
              <Link
                href={item.href}
                className="inline-flex min-h-11 items-center hover:text-foreground"
              >
                {item.label}
              </Link>
            ) : (
              <span aria-current="page" className="font-medium text-foreground">
                {item.label}
              </span>
            )}
            {i < items.length - 1 && <ChevronRight aria-hidden className="size-4 shrink-0" />}
          </li>
        ))}
      </ol>
    </nav>
  );
}

export { Breadcrumb };
