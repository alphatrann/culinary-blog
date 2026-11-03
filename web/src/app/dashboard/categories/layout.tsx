import type { ReactNode } from "react";
import { RequireAuth } from "@/components/auth/require-auth";

// The dashboard layout admits authors too; category management is admin-only (FR-CAT-003..005).
export default function CategoriesLayout({ children }: { children: ReactNode }) {
  return <RequireAuth roles={["admin"]}>{children}</RequireAuth>;
}
