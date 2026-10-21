import { Star, Trash2 } from "lucide-react";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ResponseBody } from "@/lib/api";
import { imageSrc } from "@/lib/recipes/images";

export type RecipeImage = ResponseBody<"/recipes/{recipe_id}/images", "post">;

export function ImageTile({
  image,
  index,
  busy,
  onSetPrimary,
  onDelete,
}: {
  image: RecipeImage;
  index: number;
  busy: boolean;
  onSetPrimary: () => void;
  onDelete: () => void;
}) {
  const label = image.alt_text || `Ảnh ${index + 1}`;
  return (
    <li className="flex flex-col gap-2 rounded-lg border border-border bg-background p-2">
      <div className="relative aspect-[4/3] overflow-hidden rounded-md bg-muted">
        <Image
          src={imageSrc(image)}
          alt={label}
          fill
          unoptimized
          sizes="(min-width: 640px) 220px, 45vw"
          className="object-cover"
        />
        {image.is_primary && (
          <Badge variant="count" className="absolute top-2 left-2 px-2">
            Ảnh chính
          </Badge>
        )}
        {!image.thumbnail_url && (
          <span className="absolute right-2 bottom-2 rounded-full bg-background/90 px-2 py-0.5 text-xs text-muted-foreground">
            Đang xử lý…
          </span>
        )}
      </div>
      <div className="flex items-center justify-between gap-2">
        <span className="truncate text-[13px] text-muted-foreground">{label}</span>
        <div className="flex shrink-0 gap-1">
          {!image.is_primary && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={busy}
              onClick={onSetPrimary}
              aria-label={`Đặt ${label} làm ảnh chính`}
            >
              <Star aria-hidden />
              <span className="sr-only sm:not-sr-only">Đặt làm ảnh chính</span>
            </Button>
          )}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={busy}
            onClick={onDelete}
            aria-label={`Xóa ${label}`}
          >
            <Trash2 aria-hidden />
          </Button>
        </div>
      </div>
    </li>
  );
}
