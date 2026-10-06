import Image from "next/image";
import Link from "next/link";
import { BowlIcon } from "@/components/icons/bowl-icon";
import { tintFor } from "@/components/recipes/recipe-card";
import { Badge } from "@/components/ui/badge";
import { cn } from "cn";

export type FeaturedRecipeData = {
  slug: string;
  title: string;
  description: string;
  thumbnailUrl?: string | null;
};

export function FeaturedRecipe({
  recipe,
  className,
}: {
  recipe: FeaturedRecipeData;
  className?: string;
}) {
  return (
    <Link
      href={`/recipes/${recipe.slug}`}
      data-slot="featured-recipe"
      aria-label={`Món nổi bật: ${recipe.title}`}
      className={cn(
        "group overflow-hidden rounded-xl border border-border bg-card shadow-card transition-shadow hover:shadow-card-hover",
        className,
      )}
    >
      <div
        className={cn(
          "relative flex aspect-[16/10] items-center justify-center text-muted-foreground",
          !recipe.thumbnailUrl && tintFor(recipe.slug),
        )}
      >
        {recipe.thumbnailUrl ? (
          <Image
            src={recipe.thumbnailUrl}
            alt=""
            fill
            priority
            sizes="(min-width: 1200px) 520px, 40vw"
            className="object-cover"
          />
        ) : (
          <BowlIcon aria-hidden className="size-10" strokeWidth={1.5} />
        )}
      </div>
      <div className="border-t border-border p-5">
        <Badge>Món nổi bật</Badge>
        <span className="mt-2.5 mb-1 block text-2xl font-semibold group-hover:text-primary">
          {recipe.title}
        </span>
        <span className="line-clamp-2 block text-sm leading-normal text-muted-foreground">
          {recipe.description}
        </span>
      </div>
    </Link>
  );
}
