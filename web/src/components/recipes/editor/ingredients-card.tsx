"use client";

import { Plus, Trash2 } from "lucide-react";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { FieldError, FieldHint } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import type { RecipeFormValues } from "@/lib/recipes/schemas";
import { EditorCard } from "./editor-card";

export function IngredientsCard() {
  const {
    register,
    control,
    formState: { errors },
  } = useFormContext<RecipeFormValues>();
  // `rowKey`, not the default `id`: rows carry the server id in `id` (edit mode).
  const { fields, append, remove } = useFieldArray({
    control,
    name: "ingredients",
    keyName: "rowKey",
  });

  return (
    <EditorCard title="Nguyên liệu" hint="Cần ít nhất 1 nguyên liệu để xuất bản">
      <ul className="flex flex-col gap-4">
        {fields.map((field, index) => {
          const e = errors.ingredients?.[index];
          const n = index + 1;
          return (
            <li key={field.rowKey} className="flex flex-wrap items-start gap-3">
              <div className="flex min-w-48 flex-[3] flex-col gap-1">
                <Input
                  aria-label={`Tên nguyên liệu ${n}`}
                  placeholder="Tên nguyên liệu"
                  aria-invalid={!!e?.name}
                  {...register(`ingredients.${index}.name`)}
                />
                <FieldError>{e?.name?.message}</FieldError>
              </div>
              <div className="flex w-24 flex-col gap-1">
                <Input
                  type="number"
                  step="any"
                  min={0}
                  inputMode="decimal"
                  aria-label={`Số lượng nguyên liệu ${n}`}
                  placeholder="Số lượng"
                  aria-invalid={!!e?.quantity}
                  {...register(`ingredients.${index}.quantity`)}
                />
                <FieldError>{e?.quantity?.message}</FieldError>
              </div>
              <div className="flex w-28 flex-col gap-1">
                <Input
                  aria-label={`Đơn vị nguyên liệu ${n}`}
                  placeholder="Đơn vị"
                  aria-invalid={!!e?.unit}
                  {...register(`ingredients.${index}.unit`)}
                />
                <FieldError>{e?.unit?.message}</FieldError>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                aria-label={`Xóa nguyên liệu ${n}`}
                onClick={() => remove(index)}
              >
                <Trash2 />
              </Button>
            </li>
          );
        })}
      </ul>
      {fields.length === 0 && <FieldHint>Chưa có nguyên liệu nào.</FieldHint>}
      <Button
        type="button"
        variant="outline"
        className="self-start"
        onClick={() => append({ name: "", quantity: "", unit: "" })}
      >
        <Plus /> Thêm nguyên liệu
      </Button>
    </EditorCard>
  );
}
