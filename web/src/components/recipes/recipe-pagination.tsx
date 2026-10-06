import { Pagination } from "@/components/ui/pagination";
import { buildHref } from "@/lib/list-params";

/** Adapts API list meta (`page`, `total_pages`) + the active filter params to the link-based pager. */
function RecipePagination({
  basePath,
  page,
  totalPages,
  params,
  className,
}: {
  basePath: string;
  page: number;
  totalPages: number;
  /** Active filters (`difficulty`, `max_cook_time`, `sort`, `q`, …); `page` is added per link. */
  params?: Record<string, string | number | undefined>;
  className?: string;
}) {
  return (
    <Pagination
      page={page}
      pageCount={totalPages}
      hrefFor={(p) => buildHref(basePath, { ...params, page: p })}
      className={className}
    />
  );
}

export { RecipePagination };
