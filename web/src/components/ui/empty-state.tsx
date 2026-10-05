import * as React from "react";
import { BowlIcon } from "@/components/icons/bowl-icon";
import { cn } from "cn";

function EmptyState({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      data-slot="empty-state"
      className={cn(
        "flex flex-col items-center gap-3 rounded-xl border border-border bg-card px-6 py-12 text-center",
        className,
      )}
    >
      <BowlIcon className="size-12 text-muted-foreground" strokeWidth={1.5} />
      <h2 className="text-card-title font-semibold">{title}</h2>
      {description && <p className="max-w-md text-muted-foreground">{description}</p>}
      {action}
    </div>
  );
}

export { EmptyState };
