import { describe, expect, it } from "vitest";
import { IMAGE_FORMAT_ERROR, MAX_IMAGE_BYTES, imageSrc, validateImageFile } from "./images";

describe("validateImageFile", () => {
  it.each(["image/jpeg", "image/png", "image/webp", "image/avif"])(
    "accepts %s under the limit",
    (type) => {
      expect(validateImageFile({ type, size: 1024 })).toBeNull();
    },
  );

  it("accepts exactly 5 MB", () => {
    expect(validateImageFile({ type: "image/png", size: MAX_IMAGE_BYTES })).toBeNull();
  });

  it("rejects one byte over 5 MB", () => {
    expect(validateImageFile({ type: "image/png", size: MAX_IMAGE_BYTES + 1 })).toBe(
      IMAGE_FORMAT_ERROR,
    );
  });

  it.each(["application/pdf", "image/gif", "image/svg+xml", ""])("rejects type %j", (type) => {
    expect(validateImageFile({ type, size: 1024 })).toBe(IMAGE_FORMAT_ERROR);
  });
});

describe("imageSrc", () => {
  it("prefers the thumbnail once the worker has produced it", () => {
    expect(
      imageSrc({ thumbnail_url: "https://cdn/t.webp", original_url: "https://cdn/o.jpg" }),
    ).toBe("https://cdn/t.webp");
  });

  it("falls back to the original while the worker is running", () => {
    expect(imageSrc({ thumbnail_url: null, original_url: "https://cdn/o.jpg" })).toBe(
      "https://cdn/o.jpg",
    );
  });
});
