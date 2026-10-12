"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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

  // Don't flash the form at someone who is already signed in.
  if (status === "authenticated") return null;
  return <>{children}</>;
}
