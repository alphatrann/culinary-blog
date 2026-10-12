"use client";

import { useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api, isApiError, type ResponseBody } from "@/lib/api";

export type SessionUser = ResponseBody<"/auth/me", "get">;

export type SessionStatus = "loading" | "authenticated" | "guest";

export const sessionQueryKey = ["auth", "me"] as const;

/** Mirrors the backend `Principal`: admins satisfy every role check. */
export function hasRole(user: SessionUser | null | undefined, ...roles: string[]): boolean {
  if (!user) return false;
  return user.roles.includes("admin") || roles.some((role) => user.roles.includes(role));
}

/**
 * Current user, resolved in the browser via `GET /auth/me` (cookies are never sent on SSR/ISR, so
 * public pages stay anonymous and cacheable). A 401 — after the client's silent refresh — means guest.
 */
export function useUser() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const query = useQuery({
    queryKey: sessionQueryKey,
    queryFn: async ({ signal }): Promise<SessionUser | null> => {
      try {
        return await api.get("/auth/me", { signal });
      } catch (error) {
        if (isApiError(error) && error.status === 401) return null;
        throw error;
      }
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => api.post("/auth/logout"),
    // Whether or not the server call succeeded, the browser should stop acting as signed in.
    onSettled: () => {
      queryClient.setQueryData(sessionQueryKey, null);
      queryClient.removeQueries({
        predicate: (q) => q.queryKey[0] === "auth" && q.queryKey[1] !== "me",
      });
      router.replace("/");
    },
  });
  const { mutate } = logoutMutation;
  const logout = useCallback(() => mutate(), [mutate]);

  const user = query.data ?? null;
  const status: SessionStatus = query.isPending ? "loading" : user ? "authenticated" : "guest";
  return { user, status, logout };
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  const letters = parts.length > 1 ? [parts[0], parts[parts.length - 1]] : [parts[0] ?? "?"];
  return letters
    .map((p) => p[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}
