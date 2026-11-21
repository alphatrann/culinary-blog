import type { Metadata } from "next";
import { MyRecipes } from "@/components/dashboard/my-recipes";
import { ProfileForm } from "@/components/profile/profile-form";
import type { ListSearchParams } from "@/lib/list-params";
import { parseMyRecipesParams } from "@/lib/recipes/my-recipes";

export const metadata: Metadata = { title: "Hồ sơ" };

export default async function ProfilePage({
  searchParams,
}: {
  searchParams: Promise<ListSearchParams>;
}) {
  const { tab, page } = parseMyRecipesParams(await searchParams);
  return (
    <main className="mx-auto flex w-full max-w-[1000px] flex-col gap-8 px-4 py-8 sm:px-8">
      <h1 className="text-page font-bold">Hồ sơ cá nhân</h1>
      <ProfileForm />
      <div className="flex flex-col gap-4">
        <h2 className="font-heading text-2xl font-semibold">Công thức của tôi</h2>
        <MyRecipes basePath="/profile" tab={tab} page={page} />
      </div>
    </main>
  );
}
