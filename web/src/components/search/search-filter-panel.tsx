"use client";

import * as React from "react";
import { SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { difficultyLabels, formatMinutes, type DifficultyName } from "@/lib/labels";
import { buildHref, cookTimeOptions } from "@/lib/list-params";

function RadioGroup({
  legend,
  name,
  value,
  options,
  scrollable,
}: {
  legend: string;
  name: string;
  value: string;
  options: { value: string; label: string }[];
  scrollable?: boolean;
}) {
  return (
    <fieldset className="grid gap-2">
      <legend className="mb-1 text-sm font-semibold">{legend}</legend>
      <div className={scrollable ? "grid max-h-64 gap-2 overflow-y-auto pr-1" : "grid gap-2"}>
        {options.map((o) => (
          <label key={o.value} className="flex items-center gap-2 text-sm">
            <input
              type="radio"
              name={name}
              value={o.value}
              defaultChecked={o.value === value}
              className="size-4 accent-primary"
            />
            {o.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

/**
 * GET form → `category_id`, `difficulty`, `max_cook_time` (+ hidden `q`); resets paging.
 * Always visible from 1000px; below that it sits behind a "Bộ lọc" toggle with an active-count badge.
 */
function SearchFilterPanel({
  basePath,
  q,
  categories = [],
  categoryId,
  difficulty,
  maxCookTime,
}: {
  basePath: string;
  q: string;
  categories?: { id: string; name: string }[];
  categoryId?: string;
  difficulty?: DifficultyName;
  maxCookTime?: number;
}) {
  const [open, setOpen] = React.useState(false);
  const panelId = React.useId();
  const activeCount = [categoryId, difficulty, maxCookTime].filter(Boolean).length;

  return (
    <aside aria-label="Bộ lọc" className="rounded-xl border border-border bg-card p-4">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 text-left font-semibold min-[1000px]:pointer-events-none"
      >
        <SlidersHorizontal aria-hidden="true" className="size-4" />
        Bộ lọc
        {activeCount > 0 && (
          <span
            aria-label={`${activeCount} bộ lọc đang áp dụng`}
            className="ml-auto rounded-full bg-primary px-2 text-xs text-primary-foreground"
          >
            {activeCount}
          </span>
        )}
      </button>
      <form
        id={panelId}
        action={basePath}
        method="get"
        className={`mt-4 grid gap-5 ${open ? "" : "max-[999px]:hidden"} max-[999px]:sm:grid-cols-3`}
      >
        <input type="hidden" name="q" value={q} />
        <RadioGroup
          legend="Danh mục"
          scrollable
          name="category_id"
          value={categoryId ?? ""}
          options={[
            { value: "", label: "Tất cả" },
            ...categories.map((c) => ({ value: c.id, label: c.name })),
          ]}
        />
        <RadioGroup
          legend="Độ khó"
          name="difficulty"
          value={difficulty ?? ""}
          options={[
            { value: "", label: "Tất cả" },
            ...(Object.keys(difficultyLabels) as DifficultyName[]).map((d) => ({
              value: d,
              label: difficultyLabels[d],
            })),
          ]}
        />
        <RadioGroup
          legend="Thời gian nấu"
          name="max_cook_time"
          value={maxCookTime ? String(maxCookTime) : ""}
          options={[
            { value: "", label: "Bất kỳ" },
            ...cookTimeOptions.map((m) => ({
              value: String(m),
              label: `Tối đa ${formatMinutes(m)}`,
            })),
          ]}
        />
        <div className="flex flex-wrap items-center gap-4 max-[999px]:sm:col-span-3">
          <Button type="submit">Áp dụng</Button>
          {activeCount > 0 && (
            <a href={buildHref(basePath, { q })} className="text-sm underline">
              Xóa bộ lọc
            </a>
          )}
        </div>
      </form>
    </aside>
  );
}

export { SearchFilterPanel };
