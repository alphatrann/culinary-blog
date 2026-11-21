import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { RecipeEditor } from "@/components/recipes/editor/recipe-editor";
import { Badge } from "@/components/ui/badge";

export const metadata: Metadata = { title: "Viết công thức mới" };

export default function NewRecipePage() {
  return (
    <main className="mx-auto flex w-full max-w-[1200px] flex-col gap-6 px-4 py-8 sm:px-8">
      <Link
        href="/dashboard/recipes"
        className="inline-flex min-h-11 items-center gap-2 self-start text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft aria-hidden className="size-4" /> Công thức của tôi
      </Link>
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Viết công thức mới</h1>
        <Badge>Bản nháp</Badge>
      </div>
      <RecipeEditor />
    </main>
  );
}
