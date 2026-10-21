import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { sampleRecipe } from "@/lib/recipes/recipe-fixture";
import { EditRecipeLoader } from "./edit-recipe-loader";

const get = vi.fn();
const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: { get: (...a: unknown[]) => get(...a) },
}));

function renderLoader() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <EditRecipeLoader id={sampleRecipe.id} />
    </QueryClientProvider>,
  );
}

describe("EditRecipeLoader", () => {
  beforeEach(() => {
    get.mockReset();
  });

  it("loads the recipe by id and opens the editor on it", async () => {
    get.mockImplementation((path: string) =>
      Promise.resolve(
        path === "/categories"
          ? [{ id: sampleRecipe.category_id, name: "Món chính" }]
          : sampleRecipe,
      ),
    );

    renderLoader();

    expect(await screen.findByLabelText("Tiêu đề")).toHaveValue("Phở bò Hà Nội");
    expect(get).toHaveBeenCalledWith("/recipes/{recipe_id}", {
      path: { recipe_id: sampleRecipe.id },
    });
  });

  it("explains that a non-owner cannot edit, instead of showing the editor", async () => {
    get.mockImplementation((path: string) =>
      path === "/categories"
        ? Promise.resolve([])
        : Promise.reject(new ApiError(403, { title: "Forbidden", detail: "not yours" })),
    );

    renderLoader();

    expect(await screen.findByText("Bạn không có quyền sửa công thức này")).toBeInTheDocument();
    expect(screen.queryByLabelText("Tiêu đề")).not.toBeInTheDocument();
  });

  it("says the recipe is missing on 404", async () => {
    get.mockRejectedValue(new ApiError(404, { title: "Not Found", detail: "Recipe not found" }));

    renderLoader();

    expect(await screen.findByText("Không tìm thấy công thức")).toBeInTheDocument();
  });
});
