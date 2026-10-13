import { Check, Circle } from "lucide-react";
import { Alert } from "@/components/ui/alert";
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

export function PublishCard({
  hasIngredients,
  hasSteps,
  pending,
  onSaveDraft,
  onPublish,
}: {
  hasIngredients: boolean;
  hasSteps: boolean;
  pending: "draft" | "publish" | null;
  onSaveDraft: () => void;
  onPublish: () => void;
}) {
  const ready = hasIngredients && hasSteps;
  return (
    <EditorCard title="Xuất bản">
      <ul aria-label="Điều kiện xuất bản" className="flex flex-col gap-2">
        <Item ok={hasIngredients}>Có ít nhất 1 nguyên liệu</Item>
        <Item ok={hasSteps}>Có ít nhất 1 bước thực hiện</Item>
      </ul>
      {!ready && <Alert>{PUBLISH_INCOMPLETE}</Alert>}
      <div className="flex flex-col gap-3">
        <Button type="button" disabled={!ready || pending !== null} onClick={onPublish}>
          {pending === "publish" ? "Đang xuất bản…" : "Xuất bản"}
        </Button>
        <Button type="button" variant="outline" disabled={pending !== null} onClick={onSaveDraft}>
          {pending === "draft" ? "Đang lưu…" : "Lưu nháp"}
        </Button>
      </div>
    </EditorCard>
  );
}
