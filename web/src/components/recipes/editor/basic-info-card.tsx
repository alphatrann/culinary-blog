"use client";

import { useFormContext } from "react-hook-form";
import { Field, FieldError, FieldHint, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { difficultyLabels } from "@/lib/labels";
import type { RecipeFormValues } from "@/lib/recipes/schemas";
import type { CategoryOption } from "@/lib/recipes/types";
import { EditorCard } from "./editor-card";

const difficulties = Object.values(difficultyLabels);

function NumberField({
  name,
  label,
  placeholder,
}: {
  name: "prep_time_minutes" | "cook_time_minutes" | "servings";
  label: string;
  placeholder: string;
}) {
  const {
    register,
    formState: { errors },
  } = useFormContext<RecipeFormValues>();
  return (
    <Field>
      <Label htmlFor={name}>{label}</Label>
      <Input
        id={name}
        type="number"
        inputMode="numeric"
        min={1}
        placeholder={placeholder}
        aria-invalid={!!errors[name]}
        aria-describedby={`${name}-error`}
        {...register(name)}
      />
      <FieldError id={`${name}-error`}>{errors[name]?.message}</FieldError>
    </Field>
  );
}

export function BasicInfoCard({
  categories,
  categoriesLoading,
}: {
  categories: CategoryOption[];
  categoriesLoading?: boolean;
}) {
  const {
    register,
    formState: { errors },
  } = useFormContext<RecipeFormValues>();

  return (
    <EditorCard title="Thông tin cơ bản">
      <Field>
        <Label htmlFor="title">Tiêu đề</Label>
        <Input
          id="title"
          placeholder="Ví dụ: Phở bò Hà Nội"
          aria-invalid={!!errors.title}
          aria-describedby="title-hint title-error"
          {...register("title")}
        />
        <FieldHint id="title-hint">Từ 5 đến 200 ký tự</FieldHint>
        <FieldError id="title-error">{errors.title?.message}</FieldError>
      </Field>
      <Field>
        <Label htmlFor="description">Mô tả</Label>
        <Textarea
          id="description"
          rows={3}
          aria-invalid={!!errors.description}
          aria-describedby="description-error"
          {...register("description")}
        />
        <FieldError id="description-error">{errors.description?.message}</FieldError>
      </Field>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field>
          <Label htmlFor="category_id">Danh mục</Label>
          <Select
            className="w-full"
            id="category_id"
            aria-invalid={!!errors.category_id}
            aria-describedby="category_id-error"
            {...register("category_id")}
          >
            <option value="">{categoriesLoading ? "Đang tải…" : "Chọn danh mục"}</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
          <FieldError id="category_id-error">{errors.category_id?.message}</FieldError>
        </Field>
        <Field>
          <Label htmlFor="difficulty">Độ khó</Label>
          <Select
            className="w-full"
            id="difficulty"
            aria-invalid={!!errors.difficulty}
            aria-describedby="difficulty-error"
            {...register("difficulty")}
          >
            {difficulties.map((label, i) => (
              <option key={label} value={String(i + 1)}>
                {label}
              </option>
            ))}
          </Select>
          <FieldError id="difficulty-error">{errors.difficulty?.message}</FieldError>
        </Field>
      </div>
      <div className="grid gap-5 sm:grid-cols-3">
        <NumberField name="prep_time_minutes" label="Chuẩn bị (phút)" placeholder="30" />
        <NumberField name="cook_time_minutes" label="Nấu (phút)" placeholder="180" />
        <NumberField name="servings" label="Khẩu phần" placeholder="4" />
      </div>
    </EditorCard>
  );
}
