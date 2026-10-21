"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { api, isApiError } from "@/lib/api";
import { RecipeEditor } from "./recipe-editor";

/** Loads a recipe by id for the owner or an admin, then mounts the editor in edit mode with that snapshot. */
export function EditRecipeLoader({ id }: { id: string }) {
  const queryClient = useQueryClient();
  const queryKey = ["recipe-edit", id] as const;
  const load = () => api.get("/recipes/{recipe_id}", { path: { recipe_id: id } });
  const query = useQuery({ queryKey, queryFn: load, retry: false });

  if (query.isPending) return <Skeleton className="h-96 w-full" aria-label="Đang tải công thức" />;
  if (query.isError) return <LoadError error={query.error} />;
  return (
    <RecipeEditor
      mode="edit"
      recipe={query.data}
      onReload={() => queryClient.fetchQuery({ queryKey, queryFn: load, staleTime: 0 })}
    />
  );
}

function LoadError({ error }: { error: unknown }) {
  if (isApiError(error) && error.status === 403) {
    return (
      <EmptyState
        title="Bạn không có quyền sửa công thức này"
        description="Chỉ tác giả của công thức hoặc quản trị viên mới có thể chỉnh sửa."
      />
    );
  }
  if (isApiError(error) && error.status === 404) {
    return (
      <EmptyState
        title="Không tìm thấy công thức"
        description="Công thức này không tồn tại hoặc đã bị xóa."
      />
    );
  }
  return (
    <EmptyState
      title="Không tải được công thức"
      description="Vui lòng tải lại trang sau ít phút."
    />
  );
}
