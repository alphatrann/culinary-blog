"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { hasRole, useUser } from "@/lib/session";

// Only signed-in visitors open the account menu, so its code is a separate chunk they alone download.
const UserMenu = dynamic(() => import("./user-menu").then((m) => m.UserMenu), {
  ssr: false,
  loading: () => <span aria-hidden="true" className="size-11 flex-none rounded-full bg-herb" />,
});

/** Guest actions (also the SSR output) or the signed-in user menu. */
export function HeaderActions() {
  const { user, logout } = useUser();
  const canWrite = hasRole(user, "author");

  if (!user) {
    return (
      <div className="hidden items-center gap-2 md:flex">
        <Link href="/auth/login" className={buttonVariants({ variant: "outline" })}>
          Đăng nhập
        </Link>
        <Link href="/auth/register" className={buttonVariants()}>
          Đăng ký
        </Link>
      </div>
    );
  }

  return (
    <div className="hidden items-center gap-2 md:flex">
      {canWrite && (
        <Link href="/dashboard/recipes/new" className={buttonVariants()}>
          Viết công thức
        </Link>
      )}
      <UserMenu name={user.display_name} canWrite={canWrite} onLogout={logout} />
    </div>
  );
}
