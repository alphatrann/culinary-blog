import type { Metadata } from "next";
import { CategoryAdminList } from "@/components/categories/admin/category-admin-list";

export const metadata: Metadata = { title: "Quản lý danh mục" };

export default function CategoriesAdminPage() {
  return (
    <main className="mx-auto flex w-full max-w-[900px] flex-col gap-6 px-4 py-8 sm:px-8">
      <h1 className="font-heading text-3xl font-semibold sm:text-4xl">Quản lý danh mục</h1>
      <CategoryAdminList />
    </main>
  );
}
