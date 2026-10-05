import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "cn";
import { controlClass } from "@/components/ui/input";

/** Native select (best a11y + mobile UX), styled to match the mockups. */
function Select({ className, children, ...props }: React.ComponentProps<"select">) {
  return (
    <div className={cn("relative inline-block min-w-44", className)}>
      <select
        data-slot="select"
        className={cn(controlClass, "h-11 appearance-none pr-9 pl-3")}
        {...props}
      >
        {children}
      </select>
      <ChevronDown
        aria-hidden
        className="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-muted-foreground"
      />
    </div>
  );
}

export { Select };
