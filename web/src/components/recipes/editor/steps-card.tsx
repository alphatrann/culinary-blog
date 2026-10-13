"use client";

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, Plus, Trash2 } from "lucide-react";
import { useFieldArray, useFormContext } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { FieldError, FieldHint } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import type { RecipeFormValues } from "@/lib/recipes/schemas";
import { EditorCard } from "./editor-card";

function StepRow({ id, index, onRemove }: { id: string; index: number; onRemove: () => void }) {
  const {
    register,
    formState: { errors },
  } = useFormContext<RecipeFormValues>();
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });
  const n = index + 1;
  const error = errors.steps?.[index]?.text?.message;

  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`flex items-start gap-3 ${isDragging ? "relative z-10 opacity-80" : ""}`}
    >
      <Button
        type="button"
        variant="ghost"
        size="icon"
        ref={setActivatorNodeRef}
        aria-label={`Kéo để sắp xếp bước ${n}`}
        className="touch-none"
        {...attributes}
        {...listeners}
      >
        <GripVertical />
      </Button>
      <span
        aria-hidden
        className="mt-2 flex size-7 shrink-0 items-center justify-center rounded-full bg-herb text-sm font-semibold text-herb-foreground"
      >
        {n}
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <Textarea
          rows={2}
          aria-label={`Nội dung bước ${n}`}
          aria-invalid={!!error}
          {...register(`steps.${index}.text`)}
        />
        <FieldError>{error}</FieldError>
      </div>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        aria-label={`Xóa bước ${n}`}
        onClick={onRemove}
      >
        <Trash2 />
      </Button>
    </li>
  );
}

export function StepsCard() {
  const { control } = useFormContext<RecipeFormValues>();
  const { fields, append, remove, move } = useFieldArray({ control, name: "steps" });
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function onDragEnd({ active, over }: DragEndEvent) {
    if (!over || active.id === over.id) return;
    move(
      fields.findIndex((f) => f.id === active.id),
      fields.findIndex((f) => f.id === over.id),
    );
  }

  return (
    <EditorCard
      title="Các bước thực hiện"
      hint="Cần ít nhất 1 bước để xuất bản. Dòng đầu tiên của mỗi bước dùng làm tiêu đề bước."
    >
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
        <SortableContext items={fields.map((f) => f.id)} strategy={verticalListSortingStrategy}>
          <ol className="flex flex-col gap-4">
            {fields.map((field, index) => (
              <StepRow key={field.id} id={field.id} index={index} onRemove={() => remove(index)} />
            ))}
          </ol>
        </SortableContext>
      </DndContext>
      {fields.length === 0 && <FieldHint>Chưa có bước nào.</FieldHint>}
      <Button
        type="button"
        variant="outline"
        className="self-start"
        onClick={() => append({ text: "" })}
      >
        <Plus /> Thêm bước
      </Button>
    </EditorCard>
  );
}
