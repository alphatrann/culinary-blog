import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { difficultyLabels, formatMinutes, type DifficultyName } from "@/lib/labels";
import { buildHref, cookTimeOptions, sortOptions as defaultSortOptions } from "@/lib/list-params";

const selectClass = "w-full min-w-0 min-[768px]:w-auto min-[768px]:min-w-44";

/**
 * GET form → URL params `category_id`, `difficulty`, `max_cook_time`, `sort`; works without JS and with SSR.
 * `hidden` carries params that must survive a filter change (e.g. `q` on search). Page resets to 1.
 */
function RecipeFilterBar({
  basePath,
  difficulty,
  maxCookTime,
  sort,
  categoryId,
  categories,
  sortOptions = defaultSortOptions,
  hidden,
}: {
  basePath: string;
  difficulty?: DifficultyName;
  maxCookTime?: number;
  sort?: string;
  categoryId?: string;
  /** When given, renders a category select (`category_id`). */
  categories?: { id: string; name: string }[];
  sortOptions?: readonly { value: string; label: string }[];
  hidden?: Record<string, string>;
}) {
  const active = Boolean(difficulty || maxCookTime || sort || categoryId);
  return (
    <form
      action={basePath}
      method="get"
      role="search"
      aria-label="Bộ lọc công thức"
      className="grid w-full grid-cols-2 gap-3 min-[768px]:flex min-[768px]:w-auto min-[768px]:flex-wrap min-[768px]:items-end min-[768px]:gap-4"
    >
      {Object.entries(hidden ?? {}).map(([k, v]) => (
        <input key={k} type="hidden" name={k} value={v} />
      ))}
      {categories && categories.length > 0 && (
        <label className="col-span-2 grid gap-1.5 text-sm font-medium min-[768px]:col-auto">
          Danh mục
          <Select className={selectClass} name="category_id" defaultValue={categoryId ?? ""}>
            <option value="">Tất cả</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </label>
      )}
      <label className="grid gap-1.5 text-sm font-medium">
        Độ khó
        <Select className={selectClass} name="difficulty" defaultValue={difficulty ?? ""}>
          <option value="">Tất cả</option>
          {(Object.keys(difficultyLabels) as DifficultyName[]).map((d) => (
            <option key={d} value={d}>
              {difficultyLabels[d]}
            </option>
          ))}
        </Select>
      </label>
      <label className="grid gap-1.5 text-sm font-medium">
        Thời gian nấu
        <Select
          className={selectClass}
          name="max_cook_time"
          defaultValue={maxCookTime ? String(maxCookTime) : ""}
        >
          <option value="">Bất kỳ</option>
          {cookTimeOptions.map((m) => (
            <option key={m} value={m}>
              Tối đa {formatMinutes(m)}
            </option>
          ))}
        </Select>
      </label>
      <label className="col-span-2 grid gap-1.5 text-sm font-medium min-[768px]:col-auto">
        Sắp xếp
        <Select className={selectClass} name="sort" defaultValue={sort ?? "-created_at"}>
          {sortOptions.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </Select>
      </label>
      <Button type="submit" className="col-span-2 min-[768px]:col-auto">
        Áp dụng
      </Button>
      {active && (
        <a
          href={buildHref(basePath, hidden ?? {})}
          className="col-span-2 py-3 text-center text-sm underline min-[768px]:col-auto"
        >
          Xóa bộ lọc
        </a>
      )}
    </form>
  );
}

export { RecipeFilterBar };
