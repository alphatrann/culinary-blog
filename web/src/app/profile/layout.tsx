import { Suspense, type ReactNode } from "react";
import { RequireAuth } from "@/components/auth/require-auth";

export default function ProfileLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense>
      <RequireAuth>{children}</RequireAuth>
    </Suspense>
  );
}
