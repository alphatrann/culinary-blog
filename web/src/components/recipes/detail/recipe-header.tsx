import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { RecipeActions } from "@/components/recipes/detail/recipe-actions";

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  const pick = parts.length === 1 ? [parts[0]] : [parts[0], parts[parts.length - 1]];
  return pick
    .map((p) => Array.from(p)[0])
    .join("")
    .toLocaleUpperCase("vi-VN");
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    timeZone: "Asia/Ho_Chi_Minh",
  }).format(new Date(iso));
}

type HeaderProps = {
  title: string;
  description: string;
  category: { name: string; slug: string };
  authorName: string;
  publishedAt: string | null;
};

function RecipeHeader({ title, description, category, authorName, publishedAt }: HeaderProps) {
  return (
    <header>
      <Link href={`/recipes?category=${category.slug}`} className="inline-flex">
        <Badge className="hover:bg-border">{category.name}</Badge>
      </Link>
      <h1 className="mt-4 mb-3 max-w-[860px] text-[32px] leading-[1.15] font-bold text-balance sm:text-[40px] lg:text-page">
        {title}
      </h1>
      {description && (
        <p className="m-0 max-w-[680px] text-lede text-muted-foreground">{description}</p>
      )}
      <div className="mt-6 mb-8 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span
            aria-hidden
            className="flex size-10 items-center justify-center rounded-full bg-herb text-sm font-semibold text-herb-foreground"
          >
            {initials(authorName)}
          </span>
          <div className="leading-snug">
            <span className="block font-medium">{authorName}</span>
            {publishedAt && (
              <span className="block text-muted-foreground">
                Đăng ngày {formatDate(publishedAt)}
              </span>
            )}
          </div>
        </div>
        <RecipeActions title={title} />
      </div>
    </header>
  );
}

export { RecipeHeader };
