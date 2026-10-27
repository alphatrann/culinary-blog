import { ImageResponse } from "next/og";
import { isApiError } from "@/lib/api";
import { serverGet } from "@/lib/api/server";
import {
  BrandName,
  DefaultShareCard,
  SHARE_CARD_SIZE,
  shareCardColors,
  shareCardFonts,
} from "@/lib/seo/share-card";

export const revalidate = 300;
export const alt = "Bếp Nhỏ — công thức nấu ăn";
export const size = SHARE_CARD_SIZE;
export const contentType = "image/png";

type Params = Promise<{ slug: string }>;

export default async function Image({ params }: { params: Params }) {
  const { slug } = await params;
  let recipe;
  try {
    recipe = await serverGet("/recipes/{slug}", { path: { slug }, revalidate: 300 });
  } catch (e) {
    // Same non-leaking rule as the page: unknown, draft and archived recipes get the site banner.
    if (!isApiError(e)) throw e;
    recipe = undefined;
  }
  const photo = recipe?.images.find((image) => image.is_primary) ?? recipe?.images[0];
  const fonts = shareCardFonts();
  if (!recipe || !photo) return new ImageResponse(<DefaultShareCard />, { ...size, fonts });

  return new ImageResponse(
    <div style={{ display: "flex", position: "relative", width: "100%", height: "100%" }}>
      {/* satori renders a remote <img> URL; next/image is not supported here */}
      <img
        src={photo.original_url}
        alt={recipe.title}
        width={SHARE_CARD_SIZE.width}
        height={SHARE_CARD_SIZE.height}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          padding: "64px 80px",
          background:
            "linear-gradient(to top, rgba(31,42,34,0.92) 0%, rgba(31,42,34,0.35) 60%, rgba(31,42,34,0) 100%)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignSelf: "flex-start",
            padding: "8px 20px",
            borderRadius: 999,
            background: shareCardColors.primary,
            color: shareCardColors.onPhoto,
            fontSize: 28,
          }}
        >
          {recipe.category.name}
        </div>
        <div
          style={{
            display: "flex",
            marginTop: 20,
            fontFamily: "Fraunces",
            fontWeight: 700,
            fontSize: 76,
            lineHeight: 1.1,
            color: shareCardColors.onPhoto,
          }}
        >
          {recipe.title}
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginTop: 32,
          }}
        >
          <div
            style={{
              display: "flex",
              fontFamily: "Be Vietnam Pro",
              fontSize: 30,
              color: shareCardColors.onPhoto,
            }}
          >
            {recipe.author.display_name}
          </div>
          <BrandName color={shareCardColors.onPhoto} />
        </div>
      </div>
    </div>,
    { ...size, fonts },
  );
}
