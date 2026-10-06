import Image from "next/image";
import Link from "next/link";
import { BowlIcon } from "@/components/icons/bowl-icon";
import { Skeleton } from "@/components/ui/skeleton";
import { tintFor } from "@/components/recipes/recipe-card";
import { cn } from "cn";

export type CategoryCardData = {
  slug: string;
  name: string;
  description?: string | null;
  /** Optional cover; categories without one get a stable tint like recipe placeholders. */
  imageUrl?: string | null;
  recipeCount: number;
};

function CategoryCard({ category, className }: { category: CategoryCardData; className?: string }) {
  return (
    <Link
      href={`/categories/${category.slug}`}
      data-slot="category-card"
      className={cn(
        "group block h-full overflow-hidden rounded-xl border border-border bg-card shadow-card transition-shadow hover:shadow-card-hover",
        className,
      )}
    >
      <div
        className={cn(
          "relative flex aspect-[4/3] items-center justify-center border-b border-border text-muted-foreground",
          !category.imageUrl && tintFor(category.slug),
        )}
      >
        {category.imageUrl ? (
          <Image
            src={category.imageUrl}
            alt=""
            fill
            sizes="(min-width: 1200px) 33vw, (min-width: 768px) 50vw, 100vw"
            className="object-cover"
          />
        ) : (
          <BowlIcon aria-hidden className="size-8" strokeWidth={1.5} />
        )}
      </div>
      <div className="p-4">
        <h2 className="mb-1 text-card-title font-semibold group-hover:text-primary">
          {category.name}
        </h2>
        {category.description && (
          <p className="mb-2 line-clamp-2 text-muted-foreground">{category.description}</p>
        )}
        <span className="text-xs font-semibold text-muted-foreground">
          {category.recipeCount} công thức
        </span>
      </div>
    </Link>
  );
}

const gridClass = "grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-6";

function CategoryGrid({ categories }: { categories: CategoryCardData[] }) {
  return (
    <div className={gridClass}>
      {categories.map((c) => (
        <CategoryCard key={c.slug} category={c} />
      ))}
    </div>
  );
}

function CategoryGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div role="status" aria-label="Đang tải" className={gridClass}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="overflow-hidden rounded-xl border border-border bg-card">
          <Skeleton className="aspect-[4/3] rounded-none" />
          <div className="space-y-3 p-4">
            <Skeleton className="h-5 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-1/4" />
          </div>
        </div>
      ))}
    </div>
  );
}

export { CategoryCard, CategoryGrid, CategoryGridSkeleton };
