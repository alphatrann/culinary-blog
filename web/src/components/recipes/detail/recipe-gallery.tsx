import Image from "next/image";
import { BowlIcon } from "@/components/icons/bowl-icon";
import { tintFor } from "@/components/recipes/recipe-card";
import { cn } from "cn";

export type GalleryImage = {
  id: string;
  alt_text: string | null;
  is_primary: boolean;
  order_index: number;
  original_url: string;
  medium_url: string | null;
  thumbnail_url: string | null;
};

/** Primary image first, then by order. */
function sortImages(images: GalleryImage[]): GalleryImage[] {
  return [...images].sort(
    (a, b) => Number(b.is_primary) - Number(a.is_primary) || a.order_index - b.order_index,
  );
}

function RecipeGallery({
  images,
  title,
  slug,
}: {
  images: GalleryImage[];
  title: string;
  slug: string;
}) {
  const [primary, ...rest] = sortImages(images);
  const heroSrc = primary?.medium_url ?? primary?.original_url;

  return (
    <figure className="m-0">
      <div
        className={cn(
          "relative flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl border border-border text-muted-foreground sm:aspect-video",
          !heroSrc && tintFor(slug),
        )}
      >
        {heroSrc ? (
          <Image
            src={heroSrc}
            alt={primary.alt_text ?? title}
            fill
            priority
            sizes="(min-width: 1264px) 1136px, 100vw"
            className="object-cover"
          />
        ) : (
          <div className="flex flex-col items-center gap-2">
            <BowlIcon aria-hidden className="size-12" strokeWidth={1.2} />
            <span>Ảnh món ăn đang được cập nhật</span>
          </div>
        )}
      </div>
      {rest.length > 0 && (
        <ul className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {rest.slice(0, 4).map((img) => {
            const src = img.thumbnail_url ?? img.medium_url ?? img.original_url;
            return (
              <li
                key={img.id}
                className="relative aspect-[4/3] overflow-hidden rounded-md border border-border bg-muted"
              >
                <Image
                  src={src}
                  alt={img.alt_text ?? `${title}, ảnh phụ`}
                  fill
                  sizes="(min-width: 768px) 25vw, 50vw"
                  className="object-cover"
                />
              </li>
            );
          })}
        </ul>
      )}
    </figure>
  );
}

export { RecipeGallery, sortImages };
