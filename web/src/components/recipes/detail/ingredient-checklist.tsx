"use client";

import * as React from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "cn";

export type IngredientItem = {
  id: string;
  name: string;
  quantity: number | null;
  unit: string | null;
  notes: string | null;
  order_index: number;
};

const numberFormat = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 });

/** 1.5 + "kg" → "1,5 kg"; missing quantity falls back to the unit alone. */
export function formatQuantity(item: Pick<IngredientItem, "quantity" | "unit">): string {
  const qty = item.quantity == null ? "" : numberFormat.format(item.quantity);
  return [qty, item.unit].filter(Boolean).join(" ");
}

function IngredientChecklist({ ingredients }: { ingredients: IngredientItem[] }) {
  const [checked, setChecked] = React.useState<ReadonlySet<string>>(new Set());
  const sorted = React.useMemo(
    () => [...ingredients].sort((a, b) => a.order_index - b.order_index),
    [ingredients],
  );

  function toggle(id: string) {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <section
      aria-labelledby="ingredients-heading"
      className="rounded-xl border border-border bg-card p-4 shadow-card sm:p-6"
    >
      <h2 id="ingredients-heading" className="mb-1 text-2xl font-bold">
        Nguyên liệu
      </h2>
      {sorted.length === 0 ? (
        <p className="py-3 text-muted-foreground">Công thức chưa có danh sách nguyên liệu.</p>
      ) : (
        <ul className="m-0 list-none p-0">
          {sorted.map((item) => {
            const qty = formatQuantity(item);
            const done = checked.has(item.id);
            return (
              <li key={item.id} className="border-b border-border last:border-b-0">
                <label className="flex min-h-11 cursor-pointer items-center gap-3 py-2">
                  <Checkbox checked={done} onChange={() => toggle(item.id)} />
                  <span
                    className={cn("min-w-0 flex-1", done && "text-muted-foreground line-through")}
                  >
                    {item.name}
                    {item.notes && (
                      <span className="block text-muted-foreground">{item.notes}</span>
                    )}
                  </span>
                  {qty && <span className="text-right text-muted-foreground">{qty}</span>}
                </label>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

export { IngredientChecklist };
