import { Suspense, type ReactNode } from "react";
import { RequireAuth } from "@/components/auth/require-auth";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense>
      <RequireAuth roles={["author", "admin"]}>{children}</RequireAuth>
    </Suspense>
  );
}
