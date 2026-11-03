"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Field, FieldError, FieldHint, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { api, isApiError, type ResponseBody } from "@/lib/api";
import {
  categoryFormSchema,
  emptyCategoryForm,
  toCategoryPayload,
  type CategoryFormValues,
} from "@/lib/categories/schemas";

export type AdminCategory = ResponseBody<"/categories", "get">[number];

const GENERIC = "Đã có lỗi xảy ra. Vui lòng thử lại.";

interface Props {
  open: boolean;
  /** `undefined` creates a new category; otherwise the given one is edited. */
  category?: AdminCategory;
  onOpenChange: (open: boolean) => void;
}

export function CategoryFormDialog({ open, category, onOpenChange }: Props) {
  const isEdit = category !== undefined;
  const queryClient = useQueryClient();
  const [banner, setBanner] = useState<string>();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<CategoryFormValues>({
    resolver: zodResolver(categoryFormSchema),
    defaultValues: category
      ? {
          name: category.name,
          description: category.description ?? "",
          image_url: category.image_url ?? "",
        }
      : emptyCategoryForm,
  });

  const save = useMutation({
    mutationFn: (values: CategoryFormValues) =>
      category
        ? api.put("/categories/{category_id}", {
            path: { category_id: category.id },
            body: toCategoryPayload(values),
          })
        : api.post("/categories", { body: toCategoryPayload(values) }),
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      toast.success(
        isEdit ? `Đã cập nhật danh mục “${saved.name}”.` : `Đã tạo danh mục “${saved.name}”.`,
      );
      onOpenChange(false);
    },
    onError: (error) => {
      const fieldErrors = isApiError(error) ? error.errors : {};
      for (const [field, message] of Object.entries(fieldErrors)) {
        setError(field as keyof CategoryFormValues, { message });
      }
      if (Object.keys(fieldErrors).length) return setBanner(undefined);
      setBanner(isApiError(error) && error.status === 409 ? error.detail : GENERIC);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={isEdit ? "Sửa danh mục" : "Thêm danh mục"}
        description={
          isEdit
            ? "Đổi tên không thay đổi đường dẫn (slug) hiện có."
            : "Đường dẫn được tạo tự động từ tên."
        }
      >
        <form
          noValidate
          onSubmit={handleSubmit((values) => {
            setBanner(undefined);
            save.mutate(values);
          })}
          className="flex flex-col gap-5"
        >
          {banner && <Alert>{banner}</Alert>}
          <Field>
            <Label htmlFor="category-name">Tên danh mục</Label>
            <Input
              id="category-name"
              autoComplete="off"
              aria-invalid={!!errors.name}
              aria-describedby="category-name-error"
              {...register("name")}
            />
            <FieldError id="category-name-error">{errors.name?.message}</FieldError>
          </Field>
          <Field>
            <Label htmlFor="category-description">Mô tả</Label>
            <Textarea
              id="category-description"
              maxLength={2000}
              aria-invalid={!!errors.description}
              aria-describedby="category-description-hint category-description-error"
              {...register("description")}
            />
            <FieldHint id="category-description-hint">Tối đa 2000 ký tự.</FieldHint>
            <FieldError id="category-description-error">{errors.description?.message}</FieldError>
          </Field>
          <Field>
            <Label htmlFor="category-image">Liên kết ảnh</Label>
            <Input
              id="category-image"
              type="url"
              inputMode="url"
              placeholder="https://"
              aria-invalid={!!errors.image_url}
              aria-describedby="category-image-error"
              {...register("image_url")}
            />
            <FieldError id="category-image-error">{errors.image_url?.message}</FieldError>
          </Field>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Hủy
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Đang lưu…" : "Lưu"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
