"use client";

import { useQuery } from "@tanstack/react-query";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { CategoryDeleteDialog } from "./category-delete-dialog";
import { CategoryFormDialog, type AdminCategory } from "./category-form-dialog";

/** `form`: undefined = closed, `{}` = create, `{ category }` = edit. Dialogs mount only while open so each starts fresh. */
type FormTarget = { category?: AdminCategory } | undefined;

export function CategoryAdminList() {
  const [form, setForm] = useState<FormTarget>();
  const [deleting, setDeleting] = useState<AdminCategory>();

  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/categories"),
    staleTime: 60_000,
  });

  return (
    <section aria-labelledby="categories-heading" className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="categories-heading" className="font-heading text-2xl font-semibold">
          Danh sách danh mục
        </h2>
        <Button onClick={() => setForm({})}>
          <Plus aria-hidden /> Thêm danh mục
        </Button>
      </div>

      {categories.isPending && <Skeleton className="h-40 w-full" />}
      {categories.isError && <Alert>Không tải được danh sách danh mục. Vui lòng thử lại.</Alert>}
      {categories.isSuccess && categories.data.length === 0 && (
        <EmptyState
          title="Chưa có danh mục nào"
          description="Thêm danh mục đầu tiên để phân loại công thức."
        />
      )}
      {categories.isSuccess && categories.data.length > 0 && (
        <ul className="divide-y divide-border rounded-xl border border-border bg-card">
          {categories.data.map((category) => (
            <li
              key={category.id}
              className="flex flex-wrap items-center justify-between gap-3 px-4 py-3"
            >
              <div className="flex min-w-0 flex-col">
                <span className="font-medium">{category.name}</span>
                <span className="truncate text-[13px] text-muted-foreground">
                  /{category.slug} · {category.recipe_count} công thức đã xuất bản
                </span>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  aria-label={`Sửa ${category.name}`}
                  onClick={() => setForm({ category })}
                >
                  <Pencil aria-hidden /> Sửa
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label={`Xóa ${category.name}`}
                  onClick={() => setDeleting(category)}
                >
                  <Trash2 aria-hidden /> Xóa
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {form && (
        <CategoryFormDialog
          key={form.category?.id ?? "new"}
          open
          category={form.category}
          onOpenChange={(open) => !open && setForm(undefined)}
        />
      )}
      {deleting && (
        <CategoryDeleteDialog
          key={deleting.id}
          category={deleting}
          onOpenChange={(open) => !open && setDeleting(undefined)}
        />
      )}
    </section>
  );
}
