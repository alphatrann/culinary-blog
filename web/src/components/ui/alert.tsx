import * as React from "react";
import { CircleAlert } from "lucide-react";
import { cn } from "cn";

function Alert({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      role="alert"
      data-slot="alert"
      className={cn(
        "flex gap-2.5 rounded-md border border-destructive bg-destructive-tint px-3.5 py-3 text-sm leading-normal text-destructive",
        className,
      )}
      {...props}
    >
      <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
      <div>{children}</div>
    </div>
  );
}

export { Alert };
