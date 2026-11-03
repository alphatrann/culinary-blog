"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { api, isApiError } from "@/lib/api";
import type { AdminCategory } from "./category-form-dialog";

const GENERIC = "Đã có lỗi xảy ra. Vui lòng thử lại.";
const IN_USE =
  "Không thể xóa: danh mục vẫn còn công thức. Hãy chuyển các công thức sang danh mục khác trước.";

interface Props {
  category: AdminCategory;
  onOpenChange: (open: boolean) => void;
}

export function CategoryDeleteDialog({ category, onOpenChange }: Props) {
  const queryClient = useQueryClient();
  const [banner, setBanner] = useState<string>();

  const remove = useMutation({
    mutationFn: (id: string) =>
      api.delete("/categories/{category_id}", { path: { category_id: id } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast.success(`Đã xóa danh mục “${category.name}”.`);
      setBanner(undefined);
      onOpenChange(false);
    },
    onError: (error) => {
      setBanner(isApiError(error) && error.status === 409 ? IN_USE : GENERIC);
    },
  });

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent
        title="Xóa danh mục?"
        description={`Danh mục “${category.name}” sẽ bị ẩn khỏi trang web.`}
      >
        {banner && <Alert>{banner}</Alert>}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Hủy
          </Button>
          <Button
            type="button"
            variant="destructive"
            disabled={remove.isPending}
            onClick={() => remove.mutate(category.id)}
          >
            {remove.isPending ? "Đang xóa…" : "Xóa danh mục"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
