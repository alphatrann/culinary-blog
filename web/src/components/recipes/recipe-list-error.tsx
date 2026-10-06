import { Alert } from "@/components/ui/alert";
import { isApiError } from "@/lib/api";

/** Failure state for a list fetch; shows the RFC 7807 title/detail and a way out. */
function RecipeListError({
  error,
  retryHref,
  clearHref,
}: {
  error: unknown;
  retryHref: string;
  clearHref: string;
}) {
  const api = isApiError(error) ? error : null;
  const invalidFilter = api?.status === 422;
  return (
    <Alert>
      <p className="font-semibold">
        {invalidFilter ? "Bộ lọc không hợp lệ" : "Không tải được danh sách công thức"}
      </p>
      <p>
        {invalidFilter
          ? "Một số giá trị lọc không đúng. Hãy xóa bộ lọc và thử lại."
          : (api?.detail ?? "Đã có lỗi xảy ra. Vui lòng thử lại sau.")}
      </p>
      <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
        <a href={retryHref} className="font-medium underline">
          Thử lại
        </a>
        {invalidFilter && (
          <a href={clearHref} className="font-medium underline">
            Xóa bộ lọc
          </a>
        )}
      </p>
      {api?.correlationId && <p className="mt-1 text-xs">Mã tham chiếu: {api.correlationId}</p>}
    </Alert>
  );
}

export { RecipeListError };
