import { X } from "lucide-react";
import { difficultyLabels, formatMinutes, type DifficultyName } from "@/lib/labels";
import { buildHref } from "@/lib/list-params";

type Filters = {
  category_id?: string;
  difficulty?: DifficultyName;
  max_cook_time?: number;
};

/** One removable chip per active filter; each is a plain link that drops only that param (and resets paging). */
function ActiveFilterChips({
  basePath,
  q,
  filters,
  categories = [],
}: {
  basePath: string;
  q: string;
  filters: Filters;
  categories?: { id: string; name: string }[];
}) {
  const chips: { key: keyof Filters; label: string }[] = [];
  if (filters.category_id) {
    const name = categories.find((c) => c.id === filters.category_id)?.name;
    if (name) chips.push({ key: "category_id", label: `Danh mục: ${name}` });
  }
  if (filters.difficulty) {
    chips.push({ key: "difficulty", label: `Độ khó: ${difficultyLabels[filters.difficulty]}` });
  }
  if (filters.max_cook_time) {
    chips.push({
      key: "max_cook_time",
      label: `Thời gian: tối đa ${formatMinutes(filters.max_cook_time)}`,
    });
  }
  if (chips.length === 0) return null;

  return (
    <ul aria-label="Bộ lọc đang áp dụng" className="flex flex-wrap gap-2">
      {chips.map((chip) => (
        <li key={chip.key}>
          <a
            href={buildHref(basePath, { q, ...filters, [chip.key]: undefined })}
            aria-label={`Bỏ lọc ${chip.label}`}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1 text-sm hover:bg-muted"
          >
            {chip.label}
            <X aria-hidden="true" className="size-3.5" />
          </a>
        </li>
      ))}
    </ul>
  );
}

export { ActiveFilterChips };
