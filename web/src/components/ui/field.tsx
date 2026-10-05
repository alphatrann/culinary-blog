import * as React from "react";
import { cn } from "cn";

function Label({ className, ...props }: React.ComponentProps<"label">) {
  return (
    <label
      data-slot="label"
      className={cn("text-sm leading-none font-medium", className)}
      {...props}
    />
  );
}

function FieldHint({ className, ...props }: React.ComponentProps<"p">) {
  return <p className={cn("text-[13px] text-muted-foreground", className)} {...props} />;
}

function FieldError({ className, children, ...props }: React.ComponentProps<"p">) {
  if (!children) return null;
  return (
    <p role="alert" className={cn("text-[13px] text-destructive", className)} {...props}>
      {children}
    </p>
  );
}

/** Label + control + hint/error stack. Wire `htmlFor`/`id` and `aria-describedby` on the control. */
function Field({ className, ...props }: React.ComponentProps<"div">) {
  return <div data-slot="field" className={cn("flex flex-col gap-2", className)} {...props} />;
}

export { Field, FieldError, FieldHint, Label };
