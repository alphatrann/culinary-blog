import * as React from "react";
import { BE_VIETNAM_PRO_500_B64, FRAUNCES_700_B64 } from "@/lib/seo/share-card-fonts";

export const SHARE_CARD_SIZE = { width: 1200, height: 630 };

// satori only takes inline styles, so these mirror the globals.css tokens.
export const shareCardColors = {
  background: "#fafaf6",
  foreground: "#1f2a22",
  primary: "#b82a17",
  muted: "#55615a",
  onPhoto: "#ffffff",
};

const FONT_FRAUNCES = "Fraunces";
const FONT_BODY = "Be Vietnam Pro";

// ImageResponse wants an ArrayBuffer; a Buffer view is silently ignored and the fallback font renders instead.
const decode = (b64: string) => Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)).buffer;

/** Latin + Vietnamese TTF subsets; satori cannot read the WOFF2 that next/font serves. */
export function shareCardFonts() {
  return [
    {
      name: FONT_FRAUNCES,
      data: decode(FRAUNCES_700_B64),
      weight: 700 as const,
      style: "normal" as const,
    },
    {
      name: FONT_BODY,
      data: decode(BE_VIETNAM_PRO_500_B64),
      weight: 500 as const,
      style: "normal" as const,
    },
  ];
}

export function BowlMark({ size, color }: { size: number; color: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke={color}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12h18a9 9 0 0 1-18 0z" />
      <path d="M9 8c0-1.5 1-1.5 1-3" />
      <path d="M14 8c0-1.5 1-1.5 1-3" />
    </svg>
  );
}

export function BrandName({ color }: { color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <BowlMark size={48} color={color} />
      <div
        style={{ display: "flex", fontFamily: FONT_FRAUNCES, fontWeight: 700, fontSize: 40, color }}
      >
        Bếp Nhỏ
      </div>
    </div>
  );
}

/** Site-wide banner: used by the root route and as the fallback for pages with no image of their own. */
export function DefaultShareCard() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        width: "100%",
        height: "100%",
        padding: "0 96px",
        background: shareCardColors.background,
      }}
    >
      <BowlMark size={96} color={shareCardColors.primary} />
      <div
        style={{
          display: "flex",
          marginTop: 32,
          fontFamily: FONT_FRAUNCES,
          fontWeight: 700,
          fontSize: 120,
          color: shareCardColors.foreground,
        }}
      >
        Bếp Nhỏ
      </div>
      <div
        style={{
          display: "flex",
          marginTop: 16,
          fontFamily: FONT_BODY,
          fontSize: 40,
          color: shareCardColors.muted,
        }}
      >
        Chia sẻ công thức nấu ăn
      </div>
    </div>
  );
}
