"use client";

import { AlertDialog } from "@base-ui/react/alert-dialog";
import { ImagePlus, X } from "lucide-react";
import { useId, useRef, useState } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { mapImageError } from "@/lib/recipes/errors";
import { IMAGE_ACCEPT, validateImageFile } from "@/lib/recipes/images";
import { cn } from "cn";
import { EditorCard } from "./editor-card";
import { ImageTile, type RecipeImage } from "./image-tile";

type Upload = {
  id: number;
  name: string;
  status: "uploading" | "error";
  progress: number;
  error?: string;
};

export function ImagePanel({
  recipeId,
  images,
  onChange,
}: {
  /** `null` until the recipe has a draft; the panel then renders disabled. */
  recipeId: string | null;
  images: RecipeImage[];
  onChange: (images: RecipeImage[]) => void;
}) {
  const hintId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const nextUploadId = useRef(0);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();
  const [status, setStatus] = useState("");
  const [toDelete, setToDelete] = useState<RecipeImage | null>(null);
  const disabled = recipeId === null;

  const updateUpload = (id: number, patch: Partial<Upload>) =>
    setUploads((list) => list.map((u) => (u.id === id ? { ...u, ...patch } : u)));

  async function uploadFiles(files: File[]) {
    if (!recipeId || files.length === 0) return;
    setBusy(true);
    setError(undefined);
    // Uploads run one at a time, so each response is folded into this local list before the next request.
    let current = images;
    try {
      for (const file of files) {
        const id = ++nextUploadId.current;
        const problem = validateImageFile(file);
        if (problem) {
          setUploads((list) => [
            ...list,
            { id, name: file.name, status: "error", progress: 0, error: problem },
          ]);
          continue;
        }
        setUploads((list) => [...list, { id, name: file.name, status: "uploading", progress: 0 }]);
        const formData = new FormData();
        formData.append("file", file);
        try {
          const created = await api.post("/recipes/{recipe_id}/images", {
            path: { recipe_id: recipeId },
            formData,
            onProgress: (fraction) => updateUpload(id, { progress: fraction }),
          });
          current = [...current, created];
          onChange(current);
          setUploads((list) => list.filter((u) => u.id !== id));
          setStatus(`Đã tải ảnh ${file.name}`);
        } catch (err) {
          updateUpload(id, { status: "error", error: mapImageError(err) });
        }
      }
    } finally {
      setBusy(false);
    }
  }

  async function setPrimary(image: RecipeImage) {
    if (!recipeId) return;
    setBusy(true);
    setError(undefined);
    try {
      const updated = await api.patch("/recipes/{recipe_id}/images/{image_id}/primary", {
        path: { recipe_id: recipeId, image_id: image.id },
      });
      onChange(images.map((i) => ({ ...i, is_primary: i.id === updated.id })));
      setStatus("Đã đặt ảnh chính");
    } catch (err) {
      setError(mapImageError(err));
    } finally {
      setBusy(false);
    }
  }

  async function confirmDelete() {
    const target = toDelete;
    if (!recipeId || !target) return;
    setToDelete(null);
    setBusy(true);
    setError(undefined);
    try {
      await api.delete("/recipes/{recipe_id}/images/{image_id}", {
        path: { recipe_id: recipeId, image_id: target.id },
      });
      const remaining = images.filter((i) => i.id !== target.id);
      // The server promotes the lowest order_index when the primary is deleted; mirror that so the badge is never
      // missing. A later detail refetch (#46) replaces this local copy with the server's state.
      if (target.is_primary && remaining.length > 0) {
        const next = [...remaining].sort((a, b) => a.order_index - b.order_index)[0]!;
        onChange(remaining.map((i) => ({ ...i, is_primary: i.id === next.id })));
      } else {
        onChange(remaining);
      }
      setStatus("Đã xóa ảnh");
    } catch (err) {
      setError(mapImageError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <EditorCard title="Ảnh món ăn" hint="Ảnh chính hiển thị trên danh sách và trang công thức.">
      {disabled ? (
        <p
          id={hintId}
          className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground"
        >
          Lưu nháp để thêm ảnh
        </p>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            void uploadFiles(Array.from(e.dataTransfer.files));
          }}
          className={cn(
            "flex flex-col items-center gap-2 rounded-lg border border-dashed border-border p-6 text-center",
            dragging && "bg-sage-mist border-ring",
          )}
        >
          <ImagePlus aria-hidden className="size-6 text-muted-foreground" />
          <p className="text-sm">Kéo thả ảnh vào đây hoặc</p>
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            aria-describedby={hintId}
            onClick={() => inputRef.current?.click()}
          >
            Chọn ảnh
          </Button>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept={IMAGE_ACCEPT}
            hidden
            onChange={(e) => {
              const files = Array.from(e.target.files ?? []);
              e.target.value = "";
              void uploadFiles(files);
            }}
          />
          <p id={hintId} className="text-xs text-muted-foreground">
            JPEG, PNG, WebP hoặc AVIF · tối đa 5 MB mỗi ảnh
          </p>
        </div>
      )}

      {uploads.length > 0 && (
        <ul aria-label="Tiến trình tải ảnh" className="flex flex-col gap-2">
          {uploads.map((u) => (
            <li key={u.id} className="flex flex-col gap-1 text-sm">
              <div className="flex items-center justify-between gap-2">
                <span className="truncate">{u.name}</span>
                {u.status === "error" ? (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    aria-label={`Đóng thông báo lỗi ${u.name}`}
                    onClick={() => setUploads((list) => list.filter((x) => x.id !== u.id))}
                  >
                    <X aria-hidden />
                  </Button>
                ) : (
                  <span className="text-xs text-muted-foreground">
                    {Math.round(u.progress * 100)}%
                  </span>
                )}
              </div>
              {u.status === "error" ? (
                <span className="text-xs text-destructive">{u.error}</span>
              ) : (
                <div
                  role="progressbar"
                  aria-label={`Đang tải ${u.name}`}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(u.progress * 100)}
                  className="h-1.5 overflow-hidden rounded-full bg-muted"
                >
                  <div
                    className="h-full bg-primary transition-[width]"
                    style={{ width: `${u.progress * 100}%` }}
                  />
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {error && <Alert>{error}</Alert>}

      {images.length > 0 && (
        <ul aria-label="Ảnh đã tải" className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {images.map((image, index) => (
            <ImageTile
              key={image.id}
              image={image}
              index={index}
              busy={busy}
              onSetPrimary={() => void setPrimary(image)}
              onDelete={() => setToDelete(image)}
            />
          ))}
        </ul>
      )}

      <p role="status" aria-live="polite" className="sr-only">
        {status}
      </p>

      <AlertDialog.Root
        open={toDelete !== null}
        onOpenChange={(open) => !open && setToDelete(null)}
      >
        <AlertDialog.Portal>
          <AlertDialog.Backdrop className="fixed inset-0 bg-foreground/40" />
          <AlertDialog.Popup className="fixed top-1/2 left-1/2 flex w-[min(90vw,400px)] -translate-x-1/2 -translate-y-1/2 flex-col gap-3 rounded-xl border border-border bg-card p-6 shadow-lg">
            <AlertDialog.Title className="font-heading text-lg font-semibold">
              Xóa ảnh này?
            </AlertDialog.Title>
            <AlertDialog.Description className="text-sm text-muted-foreground">
              Ảnh sẽ bị xóa khỏi công thức. Thao tác này không thể hoàn tác.
            </AlertDialog.Description>
            <div className="mt-2 flex justify-end gap-3">
              <AlertDialog.Close render={<Button variant="outline" />}>Hủy</AlertDialog.Close>
              <Button type="button" variant="destructive" onClick={() => void confirmDelete()}>
                Xóa ảnh
              </Button>
            </div>
          </AlertDialog.Popup>
        </AlertDialog.Portal>
      </AlertDialog.Root>
    </EditorCard>
  );
}
