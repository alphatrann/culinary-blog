import { Search } from "lucide-react";
import { FeaturedRecipe, type FeaturedRecipeData } from "@/components/home/featured-recipe";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

/** Headline + GET search form (works without JS); the featured card shows from 1000px up. */
export function Hero({ featured }: { featured?: FeaturedRecipeData }) {
  return (
    <section className="py-8 min-[768px]:py-12 min-[1000px]:pt-16 min-[1000px]:pb-14">
      <div className="mx-auto max-w-[1200px] px-4 min-[768px]:px-8">
        <div className="grid items-center gap-14 min-[1000px]:grid-cols-[1.1fr_0.9fr]">
          <div>
            <span className="mb-4 inline-flex h-[26px] items-center rounded-full bg-secondary px-2.5 text-xs font-semibold text-secondary-foreground">
              Công thức nấu ăn Việt
            </span>
            <h1 className="mb-4 text-[34px] leading-[1.08] font-bold tracking-[-0.01em] min-[768px]:text-[42px] min-[1000px]:text-hero">
              Món ngon cho bữa cơm nhà
            </h1>
            <p className="mb-5 max-w-[520px] text-base leading-[1.6] text-muted-foreground min-[768px]:mb-7 min-[768px]:text-lede">
              Công thức từng bước, nguyên liệu rõ ràng. Tìm món bạn muốn nấu hôm nay.
            </p>
            <form
              role="search"
              aria-label="Tìm công thức"
              action="/search"
              method="get"
              className="flex max-w-[520px] flex-col gap-2 min-[768px]:flex-row"
            >
              <div className="relative min-w-0 flex-1">
                <label htmlFor="home-q" className="sr-only">
                  Tìm công thức
                </label>
                <Search
                  aria-hidden="true"
                  className="pointer-events-none absolute top-3.5 left-3 size-4 text-muted-foreground"
                />
                <Input id="home-q" name="q" type="search" className="pl-[38px]" />
              </div>
              <Button type="submit">Tìm kiếm</Button>
            </form>
          </div>
          {featured && <FeaturedRecipe recipe={featured} className="hidden min-[1000px]:block" />}
        </div>
      </div>
    </section>
  );
}
