import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { IMAGE_FORMAT_ERROR, MAX_IMAGE_BYTES } from "@/lib/recipes/images";
import { ImagePanel } from "./image-panel";
import type { RecipeImage } from "./image-tile";

const post = vi.fn();
const patch = vi.fn();
const del = vi.fn();
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: {
    post: (...a: unknown[]) => post(...a),
    patch: (...a: unknown[]) => patch(...a),
    delete: (...a: unknown[]) => del(...a),
  },
}));

const RECIPE = "6b2f3c1e-0000-4000-8000-000000000001";

const image = (over: Partial<RecipeImage> & { id: string }): RecipeImage => ({
  alt_text: null,
  is_primary: false,
  medium_url: null,
  order_index: 0,
  original_url: `https://cdn.test/${over.id}.jpg`,
  thumbnail_url: `https://cdn.test/${over.id}-t.webp`,
  ...over,
});

const pngFile = (name = "pho.png", size = 1024) =>
  new File([new Uint8Array(size)], name, { type: "image/png" });

/** Parent that owns the list, as the editor will: `onChange` feeds the new list back in. */
function Harness({
  initial,
  onChange,
}: {
  initial: RecipeImage[];
  onChange: (images: RecipeImage[]) => void;
}) {
  const [images, setImages] = useState(initial);
  return (
    <ImagePanel
      recipeId={RECIPE}
      images={images}
      onChange={(next) => {
        setImages(next);
        onChange(next);
      }}
    />
  );
}

function fileInput(container: HTMLElement) {
  return container.querySelector<HTMLInputElement>('input[type="file"]')!;
}

describe("ImagePanel", () => {
  beforeEach(() => {
    post.mockReset();
    patch.mockReset();
    del.mockReset();
  });

  it("renders disabled until the recipe has a draft", () => {
    render(<ImagePanel recipeId={null} images={[]} onChange={vi.fn()} />);

    expect(screen.getByText("Lưu nháp để thêm ảnh")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Chọn ảnh" })).not.toBeInTheDocument();
  });

  it("rejects a non-image file on the client without calling the API", async () => {
    const { container } = render(<ImagePanel recipeId={RECIPE} images={[]} onChange={vi.fn()} />);

    fireEvent.change(fileInput(container), {
      target: { files: [new File(["x"], "menu.pdf", { type: "application/pdf" })] },
    });

    expect(await screen.findByText(IMAGE_FORMAT_ERROR)).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("rejects a file over 5 MB on the client", async () => {
    const { container } = render(<ImagePanel recipeId={RECIPE} images={[]} onChange={vi.fn()} />);

    fireEvent.change(fileInput(container), {
      target: { files: [pngFile("big.png", MAX_IMAGE_BYTES + 1)] },
    });

    expect(await screen.findByText(IMAGE_FORMAT_ERROR)).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("uploads a valid image and reports it to the parent", async () => {
    const onChange = vi.fn();
    const created = image({ id: "img-1", is_primary: true });
    post.mockResolvedValue(created);
    const { container } = render(<Harness initial={[]} onChange={onChange} />);

    fireEvent.change(fileInput(container), { target: { files: [pngFile()] } });

    await waitFor(() => expect(onChange).toHaveBeenCalledWith([created]));
    expect(post).toHaveBeenCalledWith(
      "/recipes/{recipe_id}/images",
      expect.objectContaining({ path: { recipe_id: RECIPE }, formData: expect.any(FormData) }),
    );
    expect(await screen.findByText("Ảnh chính")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Đã tải ảnh pho.png");
  });

  it("shows the server's message when the upload is rejected", async () => {
    post.mockRejectedValue(
      new ApiError(400, {
        title: "Bad Request",
        detail: "Nội dung file không khớp với định dạng ảnh đã khai báo.",
      }),
    );
    const onChange = vi.fn();
    const { container } = render(<ImagePanel recipeId={RECIPE} images={[]} onChange={onChange} />);

    fireEvent.change(fileInput(container), { target: { files: [pngFile()] } });

    expect(
      await screen.findByText("Nội dung file không khớp với định dạng ảnh đã khai báo."),
    ).toBeInTheDocument();
    expect(onChange).not.toHaveBeenCalled();
  });

  it("moves the primary flag when a non-primary image is chosen", async () => {
    const a = image({ id: "a", is_primary: true, order_index: 0, alt_text: "Phở bò" });
    const b = image({ id: "b", order_index: 1, alt_text: "Bát phở" });
    patch.mockResolvedValue({ ...b, is_primary: true });
    const onChange = vi.fn();
    render(<ImagePanel recipeId={RECIPE} images={[a, b]} onChange={onChange} />);

    await userEvent.click(screen.getByRole("button", { name: "Đặt Bát phở làm ảnh chính" }));

    expect(patch).toHaveBeenCalledWith("/recipes/{recipe_id}/images/{image_id}/primary", {
      path: { recipe_id: RECIPE, image_id: "b" },
    });
    expect(onChange).toHaveBeenCalledWith([
      expect.objectContaining({ id: "a", is_primary: false }),
      expect.objectContaining({ id: "b", is_primary: true }),
    ]);
  });

  it("confirms before deleting and promotes the next image when the primary is removed", async () => {
    const a = image({ id: "a", is_primary: true, order_index: 0, alt_text: "Phở bò" });
    const b = image({ id: "b", order_index: 1, alt_text: "Bát phở" });
    del.mockResolvedValue(undefined);
    const onChange = vi.fn();
    render(<ImagePanel recipeId={RECIPE} images={[a, b]} onChange={onChange} />);

    await userEvent.click(screen.getByRole("button", { name: "Xóa Phở bò" }));
    const dialog = await screen.findByRole("alertdialog");
    expect(del).not.toHaveBeenCalled();

    await userEvent.click(within(dialog).getByRole("button", { name: "Xóa ảnh" }));

    await waitFor(() =>
      expect(del).toHaveBeenCalledWith("/recipes/{recipe_id}/images/{image_id}", {
        path: { recipe_id: RECIPE, image_id: "a" },
      }),
    );
    expect(onChange).toHaveBeenCalledWith([expect.objectContaining({ id: "b", is_primary: true })]);
  });

  it("keeps the image when the delete dialog is cancelled", async () => {
    const a = image({ id: "a", alt_text: "Phở bò" });
    render(<ImagePanel recipeId={RECIPE} images={[a]} onChange={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: "Xóa Phở bò" }));
    const dialog = await screen.findByRole("alertdialog");
    await userEvent.click(within(dialog).getByRole("button", { name: "Hủy" }));

    await waitFor(() => expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument());
    expect(del).not.toHaveBeenCalled();
  });
});
