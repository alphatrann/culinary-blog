import Image from "next/image";
import Link from "next/link";
import { Brand } from "@/components/layout/brand";

interface AuthShellProps {
  title: string;
  subtitle: string;
  switchPrompt: string;
  switchLabel: string;
  switchHref: string;
  children: React.ReactNode;
}

export function AuthShell({
  title,
  subtitle,
  switchPrompt,
  switchLabel,
  switchHref,
  children,
}: AuthShellProps) {
  return (
    <div className="grid min-h-screen min-[1000px]:grid-cols-2 lg:grid-cols-2">
      <aside className="hidden flex-col justify-between bg-tint-1 p-10 min-[1000px]:flex">
        <Brand />
        <div className="relative mx-auto aspect-[4/3] w-full max-w-md overflow-hidden rounded-lg border border-border/60">
          <Image
            src="/auth-hero.jpg"
            alt="Tô phở bò Hà Nội"
            fill
            priority
            sizes="448px"
            className="object-cover"
          />
        </div>
        <figure>
          <blockquote className="font-heading text-[28px] leading-snug text-foreground">
            Mỗi bữa cơm nhà bắt đầu từ một công thức tử tế.
          </blockquote>
          <figcaption className="mt-3 text-sm text-muted-foreground">Bếp Nhỏ</figcaption>
        </figure>
      </aside>
      <main className="flex flex-col px-4 pt-6 pb-12 sm:px-12">
        <div className="flex items-center justify-between min-[1000px]:justify-end">
          <div className="min-[1000px]:hidden">
            <Brand />
          </div>
          <Link href={switchHref} className="text-sm font-medium text-primary hover:underline">
            {switchLabel}
          </Link>
        </div>
        <div className="mx-auto flex w-full max-w-[400px] flex-1 flex-col justify-center py-8">
          <div className="flex flex-col gap-6 sm:rounded-xl sm:border sm:border-border sm:p-8 sm:shadow-sm min-[1000px]:border-0 min-[1000px]:p-0 min-[1000px]:shadow-none">
            <header className="flex flex-col gap-2">
              <h1 className="text-2xl sm:text-[length:var(--text-section)]">{title}</h1>
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            </header>
            {children}
            <p className="text-center text-sm text-muted-foreground">
              {switchPrompt}{" "}
              <Link href={switchHref} className="font-medium text-primary hover:underline">
                {switchLabel}
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
