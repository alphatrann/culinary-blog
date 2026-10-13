import type { ReactNode } from "react";

export function EditorCard({
  title,
  hint,
  children,
  ...props
}: {
  title: string;
  hint?: string;
  children: ReactNode;
} & Omit<React.ComponentProps<"section">, "title">) {
  return (
    <section
      className="flex flex-col gap-5 rounded-xl border border-border bg-card p-4 shadow-sm sm:p-6"
      {...props}
    >
      <header className="flex flex-col gap-1">
        <h2 className="font-heading text-xl font-semibold">{title}</h2>
        {hint && <p className="text-[13px] text-muted-foreground">{hint}</p>}
      </header>
      {children}
    </section>
  );
}
