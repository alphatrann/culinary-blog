import * as React from "react";
import { cn } from "cn";

export const controlClass =
  "w-full rounded-md border border-input bg-background text-sm text-foreground placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:border-border disabled:bg-muted disabled:text-muted-foreground aria-invalid:border-destructive";

function Input({ className, type = "text", ...props }: React.ComponentProps<"input">) {
  return (
    <input
      data-slot="input"
      type={type}
      className={cn(controlClass, "h-11 px-3", className)}
      {...props}
    />
  );
}

export { Input };
