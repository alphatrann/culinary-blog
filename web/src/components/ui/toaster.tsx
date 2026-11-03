"use client";

import { Toaster as SonnerToaster } from "sonner";

/** Mount once in the root providers (NFR-USE-004). Call `toast.success` / `toast.error` from `sonner` anywhere. */
export function Toaster() {
  return (
    <SonnerToaster
      position="bottom-right"
      closeButton
      toastOptions={{
        classNames: {
          toast: "rounded-lg border border-border bg-card text-card-foreground shadow-card-hover",
          success: "text-herb",
          error: "text-destructive",
        },
      }}
    />
  );
}
