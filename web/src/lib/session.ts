"use client";

import { useCallback, useEffect, useState } from "react";
import { publicApiBaseUrl } from "@/lib/env";

export type SessionUser = {
  id: string;
  display_name: string;
  email: string;
  avatar_url: string | null;
  roles: string[];
};

/**
 * Minimal client-side session used by the header. Pages are SSR/ISR-rendered as guest (no cookies),
 * then the browser resolves `/auth/me`. To be replaced by the shared session layer (#41).
 */
export function useSession() {
  const [user, setUser] = useState<SessionUser | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${publicApiBaseUrl}/auth/me`, { credentials: "include", signal: controller.signal })
      .then((res) => (res.ok ? (res.json() as Promise<SessionUser>) : null))
      .then(setUser)
      .catch(() => {});
    return () => controller.abort();
  }, []);

  const logout = useCallback(async () => {
    await fetch(`${publicApiBaseUrl}/auth/logout`, {
      method: "POST",
      credentials: "include",
    }).catch(() => {});
    setUser(null);
    window.location.assign("/");
  }, []);

  return { user, logout };
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
