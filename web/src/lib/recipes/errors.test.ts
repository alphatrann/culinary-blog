import { describe, expect, it } from "vitest";
import { ApiError } from "@/lib/api";
import { mapImageError } from "./errors";
import { IMAGE_FORMAT_ERROR } from "./images";

const apiError = (status: number, detail = "Lỗi") => new ApiError(status, { title: "x", detail });

describe("mapImageError", () => {
  it("shows the server's Vietnamese reason for a 400", () => {
    expect(mapImageError(apiError(400, "Chỉ chấp nhận ảnh JPEG, PNG, WebP hoặc AVIF."))).toBe(
      "Chỉ chấp nhận ảnh JPEG, PNG, WebP hoặc AVIF.",
    );
  });

  it("falls back to the format message when a 400 has no detail", () => {
    expect(mapImageError(apiError(400, ""))).toBe(IMAGE_FORMAT_ERROR);
  });

  it("maps 413 to the size message", () => {
    expect(mapImageError(apiError(413))).toBe("Ảnh vượt quá dung lượng tối đa 5 MB.");
  });

  it("maps 429 to the rate-limit message", () => {
    expect(mapImageError(apiError(429))).toContain("quá nhanh");
  });

  it("maps 403 to a permission message", () => {
    expect(mapImageError(apiError(403))).toContain("không có quyền");
  });

  it("falls back to a generic message for unknown errors", () => {
    expect(mapImageError(new Error("boom"))).toBe("Đã có lỗi xảy ra. Vui lòng thử lại.");
  });
});
