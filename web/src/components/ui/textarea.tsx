import * as React from "react";
import { cn } from "cn";
import { controlClass } from "@/components/ui/input";

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(controlClass, "min-h-24 resize-y px-3 py-2.5 leading-normal", className)}
      {...props}
    />
  );
}

export { Textarea };
