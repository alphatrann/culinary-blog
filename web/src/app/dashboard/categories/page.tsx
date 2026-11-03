import type { Metadata } from "next";
import { RequireAuth } from "@/components/auth/require-auth";
import { EmptyState } from "@/components/ui/empty-state";

export const metadata: Metadata = { title: "Quản lý danh mục" };

/** Admin-only placeholder. Category management ships with S3 (#25). */
export default function CategoriesPage() {
  return (
    <RequireAuth roles={["admin"]}>
      <main className="mx-auto flex w-full max-w-[1000px] flex-col gap-6 px-4 py-8 sm:px-8">
        <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Quản lý danh mục</h1>
        <EmptyState title="Sắp ra mắt" description="Quản lý danh mục sẽ có trong phiên bản sau." />
      </main>
    </RequireAuth>
  );
}
