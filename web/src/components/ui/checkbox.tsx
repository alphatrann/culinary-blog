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
        "rounded-sm checked:bg-[url('data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2024%2024%27%20fill=%27none%27%20stroke=%27white%27%20stroke-width=%273%27%20stroke-linecap=%27round%27%20stroke-linejoin=%27round%27%3E%3Cpath%20d=%27M5%2012l5%205%209-10%27/%3E%3C/svg%3E')] checked:bg-center checked:bg-no-repeat",
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
