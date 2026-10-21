import type { Metadata } from "next";
import Link from "next/link";
import { MyRecipes } from "@/components/dashboard/my-recipes";
import { buttonVariants } from "@/components/ui/button";
import type { ListSearchParams } from "@/lib/list-params";
import { parseMyRecipesParams } from "@/lib/recipes/my-recipes";

export const metadata: Metadata = { title: "Công thức của tôi" };

export default async function MyRecipesPage({
  searchParams,
}: {
  searchParams: Promise<ListSearchParams>;
}) {
  const { tab, page } = parseMyRecipesParams(await searchParams);
  return (
    <main className="mx-auto flex w-full max-w-[1000px] flex-col gap-6 px-4 py-8 sm:px-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Công thức của tôi</h1>
        <Link href="/dashboard/recipes/new" className={buttonVariants()}>
          Công thức mới
        </Link>
      </div>
      <MyRecipes basePath="/dashboard/recipes" tab={tab} page={page} />
    </main>
  );
}
