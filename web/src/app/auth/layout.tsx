import { Suspense, type ReactNode } from "react";
import { GuestOnly } from "@/components/auth/guest-only";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense>
      <GuestOnly>{children}</GuestOnly>
    </Suspense>
  );
}
