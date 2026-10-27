import { ImageResponse } from "next/og";
import { DefaultShareCard, shareCardFonts, SHARE_CARD_SIZE } from "@/lib/seo/share-card";

export const alt = "Bếp Nhỏ — chia sẻ công thức nấu ăn";
export const size = SHARE_CARD_SIZE;
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(<DefaultShareCard />, { ...size, fonts: shareCardFonts() });
}
