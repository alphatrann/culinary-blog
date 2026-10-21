import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { EditRecipeLoader } from "@/components/recipes/editor/edit-recipe-loader";

export const metadata: Metadata = { title: "Sửa công thức" };

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default async function EditRecipePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!UUID.test(id)) notFound();

  return (
    <main className="mx-auto flex w-full max-w-[1200px] flex-col gap-6 px-4 py-8 sm:px-8">
      <Link
        href="/dashboard/recipes"
        className="inline-flex min-h-11 items-center gap-2 self-start text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft aria-hidden className="size-4" /> Công thức của tôi
      </Link>
      <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Sửa công thức</h1>
      <EditRecipeLoader id={id} />
    </main>
  );
}
