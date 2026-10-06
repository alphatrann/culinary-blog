import type { Metadata } from "next";
import Link from "next/link";
import { CategoryGrid } from "@/components/categories/category-card";
import { EmptyState } from "@/components/ui/empty-state";
import { serverGet } from "@/lib/api/server";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Danh mục | Culinary Blog",
  description: "Duyệt công thức nấu ăn theo danh mục món.",
};

async function loadCategories() {
  try {
    return await serverGet("/categories", { revalidate: 3600 });
  } catch {
    // The build and first render must work with no live API; show the error state instead of failing.
    return null;
  }
}

export default async function CategoriesPage() {
  const categories = await loadCategories();

  return (
    <main className="mx-auto max-w-[1200px] px-4 py-10 sm:px-8 sm:py-12">
      <header className="mb-8 max-w-2xl">
        <h1 className="mb-3 text-page font-bold">Danh mục</h1>
        <p className="text-lede text-pretty text-muted-foreground">
          Chọn loại món bạn muốn nấu hôm nay, từ món nước, món xào đến món tráng miệng.
        </p>
      </header>
      {categories === null ? (
        <EmptyState
          title="Không tải được danh mục"
          description="Đã có lỗi khi tải danh sách. Vui lòng thử lại sau ít phút."
          action={
            <Link
              href="/recipes"
              className="font-medium text-herb underline-offset-4 hover:underline"
            >
              Xem tất cả công thức
            </Link>
          }
        />
      ) : categories.length === 0 ? (
        <EmptyState
          title="Chưa có danh mục nào"
          description="Các danh mục sẽ xuất hiện ở đây khi được tạo."
        />
      ) : (
        <CategoryGrid
          categories={categories.map((c) => ({
            slug: c.slug,
            name: c.name,
            description: c.description,
            imageUrl: c.image_url,
            recipeCount: c.recipe_count,
          }))}
        />
      )}
    </main>
  );
}
