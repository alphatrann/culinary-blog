import Image from "next/image";
import Link from "next/link";
import { BarChart3, Clock } from "lucide-react";
import { BowlIcon } from "@/components/icons/bowl-icon";
import { Badge } from "@/components/ui/badge";
import { cn } from "cn";

export type RecipeCardData = {
  slug: string;
  title: string;
  category?: string;
  /** Thumbnail variant from the image worker; absent until the worker finishes. */
  thumbnailUrl?: string | null;
  /** Total of prep + cook, already formatted (see `formatMinutes`). */
  time: string;
  difficulty: string;
  author?: string;
};

const tints = [
  "bg-tint-1",
  "bg-tint-2",
  "bg-tint-3",
  "bg-tint-4",
  "bg-tint-5",
  "bg-tint-6",
  "bg-tint-7",
  "bg-tint-8",
];

/** Stable placeholder tint per recipe so the grid doesn't flicker between renders. */
export function tintFor(key: string): string {
  let h = 0;
  for (const c of key) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return tints[h % tints.length];
}

function RecipeCard({ recipe, className }: { recipe: RecipeCardData; className?: string }) {
  return (
    <Link
      href={`/recipes/${recipe.slug}`}
      data-slot="recipe-card"
      className={cn(
        "group block h-full overflow-hidden rounded-xl border border-border bg-card shadow-card transition-shadow hover:shadow-card-hover",
        className,
      )}
    >
      <div
        className={cn(
          "relative flex aspect-[4/3] items-center justify-center border-b border-border text-muted-foreground",
          !recipe.thumbnailUrl && tintFor(recipe.slug),
        )}
      >
        {recipe.category && (
          <Badge variant="overlay" className="absolute top-3 left-3 z-10">
            {recipe.category}
          </Badge>
        )}
        {recipe.thumbnailUrl ? (
          <Image
            src={recipe.thumbnailUrl}
            alt={recipe.title}
            fill
            sizes="(min-width: 1200px) 25vw, (min-width: 768px) 33vw, 100vw"
            className="object-cover"
          />
        ) : (
          <BowlIcon aria-hidden className="size-8" strokeWidth={1.5} />
        )}
      </div>
      <div className="p-4">
        <h3 className="mb-2 text-card-title font-semibold group-hover:text-primary">
          {recipe.title}
        </h3>
        <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <Clock aria-hidden className="size-4" />
            {recipe.time}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <BarChart3 aria-hidden className="size-4" />
            {recipe.difficulty}
          </span>
        </div>
        {recipe.author && (
          <span className="mt-2 block text-muted-foreground">Bởi {recipe.author}</span>
        )}
      </div>
    </Link>
  );
}

export { RecipeCard };
