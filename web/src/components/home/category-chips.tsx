import Link from "next/link";
import { cn } from "cn";

const chipClass =
  "inline-flex h-11 flex-none items-center rounded-md border border-input bg-background px-4 text-sm font-medium whitespace-nowrap text-foreground hover:bg-accent";
const chipOnClass = "border-herb bg-herb text-herb-foreground hover:bg-herb";

/** "Tất cả" (the recipe list) + one link per category; scrolls horizontally on phones. */
export function CategoryChips({ categories }: { categories: { slug: string; name: string }[] }) {
  return (
    <nav aria-label="Danh mục">
      <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-2 min-[768px]:mx-0 min-[768px]:flex-wrap min-[768px]:overflow-visible min-[768px]:px-0 min-[768px]:pb-0">
        <Link href="/recipes" aria-current="page" className={cn(chipClass, chipOnClass)}>
          Tất cả
        </Link>
        {categories.map((c) => (
          <Link key={c.slug} href={`/categories/${c.slug}`} className={chipClass}>
            {c.name}
          </Link>
        ))}
      </div>
    </nav>
  );
}
