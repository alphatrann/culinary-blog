"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";
import { api } from "@/lib/api";
import { makeQueryClient } from "@/lib/query-client";
import { sessionQueryKey } from "@/lib/session";

export function Providers({ children }: { children: ReactNode }) {
  // useState keeps one client per browser session and a fresh one per SSR request.
  const [queryClient] = useState(makeQueryClient);

  // Refresh failed → mark the session as guest (route guards redirect) and drop other cached user data.
  useEffect(
    () =>
      api.onSignedOut(() => {
        queryClient.removeQueries({ predicate: (q) => q.queryKey[0] === "auth" });
        queryClient.setQueryData(sessionQueryKey, null);
      }),
    [queryClient],
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
