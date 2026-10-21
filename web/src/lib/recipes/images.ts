/** Mirrors the API limits (CONS-007): 5 MB, JPEG/PNG/WebP/AVIF. The server re-checks magic bytes. */
export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

export const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/avif"] as const;

export const IMAGE_ACCEPT = ALLOWED_IMAGE_TYPES.join(",");

export const IMAGE_FORMAT_ERROR = "Định dạng không hợp lệ hoặc vượt quá 5 MB";

/** Client-side pre-check so obvious rejects never leave the browser. Returns the message to show, or null. */
export function validateImageFile(file: Pick<File, "type" | "size">): string | null {
  const allowed = (ALLOWED_IMAGE_TYPES as readonly string[]).includes(file.type);
  return allowed && file.size <= MAX_IMAGE_BYTES ? null : IMAGE_FORMAT_ERROR;
}

/** Best available source for an image tile: the thumbnail once the worker has produced it, else the original. */
export function imageSrc(image: { thumbnail_url: string | null; original_url: string }): string {
  return image.thumbnail_url ?? image.original_url;
}
