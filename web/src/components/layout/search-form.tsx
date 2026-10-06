import { Search } from "lucide-react";
import { cn } from "cn";
import { Input } from "@/components/ui/input";

/** Plain GET form so search works without JS. */
export function SearchForm({ id, className }: { id: string; className?: string }) {
  return (
    <form role="search" action="/search" method="get" className={cn("relative", className)}>
      <label htmlFor={id} className="sr-only">
        Tìm công thức
      </label>
      <Search
        aria-hidden="true"
        className="pointer-events-none absolute top-3.5 left-3 size-4 text-muted-foreground"
      />
      <Input id={id} name="q" type="search" placeholder="Tìm công thức" className="pl-[38px]" />
    </form>
  );
}
