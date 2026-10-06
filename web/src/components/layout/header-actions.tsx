"use client";

import Link from "next/link";
import { Menu } from "@base-ui/react/menu";
import { LogOut, User, UtensilsCrossed } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { initials, useSession } from "@/lib/session";

const avatarClass =
  "flex size-11 flex-none items-center justify-center rounded-full bg-herb text-sm font-semibold text-herb-foreground hover:bg-herb-hover";
const itemClass =
  "flex min-h-11 w-full cursor-default items-center gap-2 rounded-md px-3 text-sm text-foreground outline-none data-[highlighted]:bg-accent";

/** Guest actions (also the SSR output) or the signed-in user menu. */
export function HeaderActions() {
  const { user, logout } = useSession();

  if (!user) {
    return (
      <div className="hidden items-center gap-2 md:flex">
        <Link href="/login" className={buttonVariants({ variant: "outline" })}>
          Đăng nhập
        </Link>
        <Link href="/register" className={buttonVariants()}>
          Đăng ký
        </Link>
      </div>
    );
  }

  return (
    <div className="hidden items-center gap-2 md:flex">
      <Link href="/recipes/new" className={buttonVariants()}>
        Viết công thức
      </Link>
      <Menu.Root>
        <Menu.Trigger className={avatarClass} aria-label="Menu tài khoản">
          {initials(user.display_name)}
        </Menu.Trigger>
        <Menu.Portal>
          <Menu.Positioner align="end" sideOffset={8} className="z-50">
            <Menu.Popup className="min-w-52 rounded-md border border-border bg-popover p-1 shadow-md">
              <div className="truncate px-3 py-2 text-sm font-semibold">{user.display_name}</div>
              <Menu.Item render={<Link href="/profile" />} className={itemClass}>
                <User className="size-4" aria-hidden="true" /> Hồ sơ
              </Menu.Item>
              <Menu.Item render={<Link href="/my-recipes" />} className={itemClass}>
                <UtensilsCrossed className="size-4" aria-hidden="true" /> Công thức của tôi
              </Menu.Item>
              <Menu.Item onClick={logout} className={itemClass}>
                <LogOut className="size-4" aria-hidden="true" /> Đăng xuất
              </Menu.Item>
            </Menu.Popup>
          </Menu.Positioner>
        </Menu.Portal>
      </Menu.Root>
    </div>
  );
}
