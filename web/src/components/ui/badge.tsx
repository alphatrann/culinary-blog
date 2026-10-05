import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "cn";

const badgeVariants = cva(
  "inline-flex h-6 items-center justify-center gap-1 rounded-full border border-transparent px-2.5 text-xs font-semibold whitespace-nowrap",
  {
    variants: {
      variant: {
        secondary: "bg-secondary text-secondary-foreground",
        outline: "border-input bg-card text-foreground",
        archived: "bg-muted text-muted-foreground",
        overlay: "border-border bg-background text-foreground",
        count: "min-w-[22px] bg-herb px-1.5 text-herb-foreground",
      },
    },
    defaultVariants: { variant: "secondary" },
  },
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return (
    <span data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
