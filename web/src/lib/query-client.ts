import { QueryClient } from "@tanstack/react-query";
import { isApiError } from "@/lib/api";

/** 4xx responses are deterministic (and 401 was already refreshed by the client); only retry transient failures. */
function shouldRetry(failureCount: number, error: unknown): boolean {
  if (isApiError(error) && error.status >= 400 && error.status < 500) return false;
  return failureCount < 2;
}

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { staleTime: 60_000, retry: shouldRetry, refetchOnWindowFocus: false },
      mutations: { retry: false },
    },
  });
}
