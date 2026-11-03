"use client";

import { AlertDialog } from "@base-ui/react/alert-dialog";
import { Check, Circle } from "lucide-react";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PUBLISH_INCOMPLETE } from "@/lib/recipes/errors";
import { EditorCard } from "./editor-card";

function Item({ ok, children }: { ok: boolean; children: string }) {
  return (
    <li className="flex items-center gap-2 text-sm">
      {ok ? (
        <Check aria-hidden className="size-4 text-herb" />
      ) : (
        <Circle aria-hidden className="size-4 text-muted-foreground" />
      )}
      <span className={ok ? "text-foreground" : "text-muted-foreground"}>
        {children}
        <span className="sr-only">{ok ? " (đã đạt)" : " (chưa đạt)"}</span>
      </span>
    </li>
  );
}

/** Edit-mode controls. The create page leaves this undefined and uses the draft/publish pair instead. */
export interface EditControls {
  published: boolean;
  dirty: boolean;
  onSave: () => void;
  onPublishToggle: () => void;
  onDelete: () => void;
}

export function PublishCard({
  hasIngredients,
  hasSteps,
  pending,
  onSaveDraft,
  onPublish,
  edit,
}: {
  hasIngredients: boolean;
  hasSteps: boolean;
  pending: string | null;
  onSaveDraft: () => void;
  onPublish: () => void;
  edit?: EditControls;
}) {
  const ready = hasIngredients && hasSteps;
  return (
    <EditorCard title="Xuất bản">
      {edit && (
        <Badge variant={edit.published ? "count" : "outline"} className="self-start">
          {edit.published ? "Đã xuất bản" : "Bản nháp"}
        </Badge>
      )}
      <ul aria-label="Điều kiện xuất bản" className="flex flex-col gap-2">
        <Item ok={hasIngredients}>Có ít nhất 1 nguyên liệu</Item>
        <Item ok={hasSteps}>Có ít nhất 1 bước thực hiện</Item>
      </ul>
      {!ready && <Alert>{PUBLISH_INCOMPLETE}</Alert>}
      {edit ? (
        <div className="flex flex-col gap-3">
          <Button type="button" disabled={!edit.dirty || pending !== null} onClick={edit.onSave}>
            {pending === "save" ? "Đang lưu…" : "Lưu thay đổi"}
          </Button>
          {edit.dirty && (
            <p className="text-[13px] text-muted-foreground">
              Lưu thay đổi trước khi xuất bản hoặc gỡ xuất bản.
            </p>
          )}
          {edit.published ? (
            <Button
              type="button"
              variant="outline"
              disabled={edit.dirty || pending !== null}
              onClick={edit.onPublishToggle}
            >
              {pending === "unpublish" ? "Đang gỡ…" : "Gỡ xuất bản"}
            </Button>
          ) : (
            <Button
              type="button"
              variant="outline"
              disabled={!ready || edit.dirty || pending !== null}
              onClick={edit.onPublishToggle}
            >
              {pending === "publish" ? "Đang xuất bản…" : "Xuất bản"}
            </Button>
          )}
          <DeleteRecipe pending={pending === "delete"} onConfirm={edit.onDelete} />
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <Button type="button" disabled={!ready || pending !== null} onClick={onPublish}>
            {pending === "publish" ? "Đang xuất bản…" : "Xuất bản"}
          </Button>
          <Button type="button" variant="outline" disabled={pending !== null} onClick={onSaveDraft}>
            {pending === "draft" ? "Đang lưu…" : "Lưu nháp"}
          </Button>
        </div>
      )}
    </EditorCard>
  );
}

function DeleteRecipe({ pending, onConfirm }: { pending: boolean; onConfirm: () => void }) {
  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger render={<Button type="button" variant="ghost" disabled={pending} />}>
        {pending ? "Đang xóa…" : "Xóa công thức"}
      </AlertDialog.Trigger>
      <AlertDialog.Portal>
        <AlertDialog.Backdrop className="fixed inset-0 bg-foreground/40" />
        <AlertDialog.Popup className="fixed top-1/2 left-1/2 flex w-[min(90vw,400px)] -translate-x-1/2 -translate-y-1/2 flex-col gap-3 rounded-xl border border-border bg-card p-6 shadow-lg">
          <AlertDialog.Title className="font-heading text-lg font-semibold">
            Xóa công thức này?
          </AlertDialog.Title>
          <AlertDialog.Description className="text-sm text-muted-foreground">
            Công thức và toàn bộ ảnh sẽ bị xóa khỏi trang web. Thao tác này không thể hoàn tác.
          </AlertDialog.Description>
          <div className="mt-2 flex justify-end gap-3">
            <AlertDialog.Close render={<Button variant="outline" />}>Hủy</AlertDialog.Close>
            <AlertDialog.Close
              render={<Button type="button" variant="destructive" onClick={onConfirm} />}
            >
              Xóa công thức
            </AlertDialog.Close>
          </div>
        </AlertDialog.Popup>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
