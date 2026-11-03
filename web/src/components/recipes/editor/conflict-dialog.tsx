"use client";

import { AlertDialog } from "@base-ui/react/alert-dialog";
import { Button } from "@/components/ui/button";

/**
 * Shown when the recipe changed on the server since this form was loaded (a 409 on save). Nothing was written,
 * so the user chooses which version wins.
 */
export function ConflictDialog({
  open,
  busy,
  onReload,
  onOverwrite,
}: {
  open: boolean;
  busy: boolean;
  onReload: () => void;
  onOverwrite: () => void;
}) {
  return (
    <AlertDialog.Root open={open}>
      <AlertDialog.Portal>
        <AlertDialog.Backdrop className="fixed inset-0 bg-foreground/40" />
        <AlertDialog.Popup className="fixed top-1/2 left-1/2 flex w-[min(90vw,440px)] -translate-x-1/2 -translate-y-1/2 flex-col gap-3 rounded-xl border border-border bg-card p-6 shadow-lg">
          <AlertDialog.Title className="font-heading text-lg font-semibold">
            Công thức đã thay đổi
          </AlertDialog.Title>
          <AlertDialog.Description className="text-sm text-muted-foreground">
            Công thức này vừa được lưu ở nơi khác sau khi bạn mở trang. Bạn có thể tải phiên bản mới
            (thay thế các chỉnh sửa chưa lưu của bạn) hoặc ghi đè bằng phiên bản của bạn.
          </AlertDialog.Description>
          <div className="mt-2 flex flex-wrap justify-end gap-3">
            <Button type="button" variant="outline" disabled={busy} onClick={onReload}>
              Tải phiên bản mới
            </Button>
            <Button type="button" variant="destructive" disabled={busy} onClick={onOverwrite}>
              Ghi đè bằng bản của tôi
            </Button>
          </div>
        </AlertDialog.Popup>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
