"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { api } from "@/lib/api";
import { makeQueryClient } from "@/lib/query-client";

export function Providers({ children }: { children: ReactNode }) {
  // useState keeps one client per browser session and a fresh one per SSR request.
  const [queryClient] = useState(makeQueryClient);

  // Refresh failed → drop cached user data so the UI falls back to the signed-out state.
  useEffect(
    () => api.onSignedOut(() => queryClient.removeQueries({ queryKey: ["auth"] })),
    [queryClient],
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
