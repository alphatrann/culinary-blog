import * as React from "react";
import { cn } from "cn";

const base =
  "size-4 shrink-0 appearance-none border border-herb bg-background transition-colors checked:bg-herb disabled:opacity-50";

function Checkbox({ className, ...props }: Omit<React.ComponentProps<"input">, "type">) {
  return (
    <input
      data-slot="checkbox"
      type="checkbox"
      className={cn(
        base,
        "checked:bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22white%22 stroke-width=%223%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22><path d=%22M5 12l5 5 9-10%22/></svg>')] rounded-sm checked:bg-center checked:bg-no-repeat",
        className,
      )}
      {...props}
    />
  );
}

function Radio({ className, ...props }: Omit<React.ComponentProps<"input">, "type">) {
  return (
    <input
      data-slot="radio"
      type="radio"
      className={cn(
        base,
        "rounded-full checked:bg-background checked:bg-herb checked:shadow-[inset_0_0_0_3px_var(--background)]",
        className,
      )}
      {...props}
    />
  );
}

export { Checkbox, Radio };
