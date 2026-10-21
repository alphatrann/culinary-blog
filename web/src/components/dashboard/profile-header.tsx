"use client";

import { Skeleton } from "@/components/ui/skeleton";
import { hasRole, initials, useUser } from "@/lib/session";

/** Read-only header: display name and role. Editing name, avatar and bio ships with S2 (#24). */
export function ProfileHeader() {
  const { user, status } = useUser();
  if (status !== "authenticated" || !user)
    return <Skeleton className="h-20 w-full" aria-label="Đang tải hồ sơ" />;
  return (
    <header className="flex items-center gap-4">
      <div
        aria-hidden
        className="flex size-16 shrink-0 items-center justify-center rounded-full bg-secondary font-heading text-xl font-semibold text-secondary-foreground"
      >
        {initials(user.display_name)}
      </div>
      <div className="min-w-0">
        <h1 className="truncate font-heading text-3xl font-semibold sm:text-4xl">
          {user.display_name}
        </h1>
        <p className="text-sm text-muted-foreground">
          {hasRole(user, "author") ? "Tác giả" : "Độc giả"}
        </p>
      </div>
    </header>
  );
}
