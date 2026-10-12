"use client";

import Link from "next/link";
import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { buttonVariants } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { loginUrl } from "@/lib/auth/next-url";
import { hasRole, useUser } from "@/lib/session";

/**
 * Client route guard. Renders nothing protected until the session resolves; guests go to the login
 * page with `?next=`, signed-in users lacking one of `roles` (any-of) see a 403 state.
 */
export function RequireAuth({ roles, children }: { roles?: string[]; children: ReactNode }) {
  const { user, status } = useUser();
  const router = useRouter();
  const pathname = usePathname();
  const search = useSearchParams().toString();

  useEffect(() => {
    if (status === "guest") router.replace(loginUrl(search ? `${pathname}?${search}` : pathname));
  }, [status, router, pathname, search]);

  if (status !== "authenticated") {
    return (
      <div className="mx-auto w-full max-w-5xl px-4 py-10" aria-busy="true">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="mt-6 h-40 w-full" />
      </div>
    );
  }

  if (roles && !hasRole(user, ...roles)) {
    return (
      <div className="mx-auto w-full max-w-5xl px-4 py-10">
        <EmptyState
          title="Bạn không có quyền truy cập trang này"
          description="Tài khoản của bạn chưa được cấp quyền cần thiết."
          action={
            <Link href="/" className={buttonVariants({ variant: "outline" })}>
              Về trang chủ
            </Link>
          }
        />
      </div>
    );
  }

  return <>{children}</>;
}
