"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Brand } from "@/components/layout/brand";
import { safeNext } from "@/lib/auth/next-url";
import { useUser } from "@/lib/session";

/** Auth pages (`/auth/*`) are for guests; signed-in users are sent on to `?next=` or home. */
export function GuestOnly({ children }: { children: ReactNode }) {
  const { status } = useUser();
  const router = useRouter();
  const next = useSearchParams().get("next");

  useEffect(() => {
    if (status === "authenticated") router.replace(safeNext(next) ?? "/");
  }, [status, next, router]);

  // Don't flash the form at someone who is already signed in; show progress while the redirect loads.
  if (status === "authenticated") {
    return (
      <div
        role="status"
        aria-busy="true"
        className="flex min-h-screen flex-col items-center justify-center gap-6"
      >
        <Brand />
        <span
          aria-hidden
          className="size-8 animate-spin rounded-full border-2 border-border border-t-primary"
        />
        <p className="text-sm text-muted-foreground">Đang chuyển hướng…</p>
      </div>
    );
  }
  return <>{children}</>;
}
