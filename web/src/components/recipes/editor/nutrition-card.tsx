"use client";

import { useFormContext } from "react-hook-form";
import { Field, FieldError, Label } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import type { RecipeFormValues } from "@/lib/recipes/schemas";
import { EditorCard } from "./editor-card";

const fields = [
  { name: "calories", label: "Năng lượng (kcal)" },
  { name: "protein", label: "Đạm (g)" },
  { name: "fat", label: "Chất béo (g)" },
  { name: "carbohydrates", label: "Tinh bột (g)" },
] as const;

export function NutritionCard() {
  const {
    register,
    formState: { errors },
  } = useFormContext<RecipeFormValues>();
  return (
    <EditorCard title="Dinh dưỡng" hint="Không bắt buộc, tính cho mỗi khẩu phần.">
      <div className="grid grid-cols-2 gap-4">
        {fields.map(({ name, label }) => (
          <Field key={name}>
            <Label htmlFor={`nutrition-${name}`}>{label}</Label>
            <Input
              id={`nutrition-${name}`}
              type="number"
              step="any"
              min={0}
              inputMode="decimal"
              aria-invalid={!!errors.nutrition?.[name]}
              aria-describedby={`nutrition-${name}-error`}
              {...register(`nutrition.${name}`)}
            />
            <FieldError id={`nutrition-${name}-error`}>
              {errors.nutrition?.[name]?.message}
            </FieldError>
          </Field>
        ))}
      </div>
    </EditorCard>
  );
}
