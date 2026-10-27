"use client";

import Link from "next/link";
import { Menu } from "@base-ui/react/menu";
import { LogOut, User, UtensilsCrossed } from "lucide-react";
import { initials, type useUser } from "@/lib/session";

const avatarClass =
  "flex size-11 flex-none items-center justify-center rounded-full bg-herb text-sm font-semibold text-herb-foreground hover:bg-herb-hover";
const itemClass =
  "flex min-h-11 w-full cursor-default items-center gap-2 rounded-md px-3 text-sm text-foreground outline-none data-[highlighted]:bg-accent";

/**
 * The signed-in account menu. Loaded on demand from HeaderActions, so guests (most visitors) never download
 * the menu code.
 */
export function UserMenu({
  name,
  canWrite,
  onLogout,
}: {
  name: string;
  canWrite: boolean;
  onLogout: ReturnType<typeof useUser>["logout"];
}) {
  return (
    <Menu.Root>
      <Menu.Trigger className={avatarClass} aria-label={`Menu tài khoản ${initials(name)}`}>
        {initials(name)}
      </Menu.Trigger>
      <Menu.Portal>
        <Menu.Positioner align="end" sideOffset={8} className="z-50">
          <Menu.Popup className="min-w-52 rounded-md border border-border bg-popover p-1 shadow-md">
            <div className="truncate px-3 py-2 text-sm font-semibold">{name}</div>
            <Menu.Item render={<Link href="/profile" />} className={itemClass}>
              <User className="size-4" aria-hidden="true" /> Hồ sơ
            </Menu.Item>
            {canWrite && (
              <Menu.Item render={<Link href="/dashboard/recipes" />} className={itemClass}>
                <UtensilsCrossed className="size-4" aria-hidden="true" /> Công thức của tôi
              </Menu.Item>
            )}
            <Menu.Item onClick={onLogout} className={itemClass}>
              <LogOut className="size-4" aria-hidden="true" /> Đăng xuất
            </Menu.Item>
          </Menu.Popup>
        </Menu.Positioner>
      </Menu.Portal>
    </Menu.Root>
  );
}
