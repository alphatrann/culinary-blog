"use client";

import { useEffect, useRef } from "react";
import { GoogleIcon } from "@/components/icons/google-icon";
import { Button } from "@/components/ui/button";

const GIS_SRC = "https://accounts.google.com/gsi/client";
const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
const FALLBACK_WIDTH = 320;

interface GoogleIdentity {
  accounts: {
    id: {
      initialize(options: {
        client_id: string;
        callback: (response: { credential: string }) => void;
      }): void;
      renderButton(parent: HTMLElement, options: Record<string, string | number>): void;
    };
  };
}

declare global {
  interface Window {
    google?: GoogleIdentity;
  }
}

/**
 * "Sign in with Google" (FR-AUTH-003). Renders nothing unless NEXT_PUBLIC_GOOGLE_CLIENT_ID is set.
 *
 * Google's button is an iframe we can't style, so it sits transparently over our shadcn button and receives the click.
 */
export function GoogleSignInButton({ onCredential }: { onCredential: (idToken: string) => void }) {
  const container = useRef<HTMLDivElement>(null);
  const callback = useRef(onCredential);
  callback.current = onCredential;

  useEffect(() => {
    const host = container.current;
    if (!CLIENT_ID || !host) return;

    // GIS draws an iframe whose width is fixed at render time, so re-render whenever the form resizes.
    const render = () => {
      if (!window.google) return;
      host.replaceChildren();
      window.google.accounts.id.renderButton(host, {
        theme: "outline",
        size: "large",
        text: "continue_with",
        width: Math.min(host.clientWidth || FALLBACK_WIDTH, 400),
      });
    };
    const mount = () => {
      if (!window.google) return;
      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: (response) => callback.current(response.credential),
      });
      render();
    };

    const observer = new ResizeObserver(render);
    observer.observe(host);

    if (window.google) {
      mount();
      return () => observer.disconnect();
    }
    const script = document.createElement("script");
    script.src = GIS_SRC;
    script.async = true;
    script.addEventListener("load", mount);
    document.head.appendChild(script);
    return () => {
      observer.disconnect();
      script.removeEventListener("load", mount);
    };
  }, []);

  if (!CLIENT_ID) return null;
  return (
    <>
      <div className="flex items-center gap-3 text-xs tracking-wider text-muted-foreground uppercase before:h-px before:flex-1 before:bg-border after:h-px after:flex-1 after:bg-border">
        Hoặc
      </div>
      <div className="group relative w-full rounded-md focus-within:ring-2 focus-within:ring-ring">
        <Button
          type="button"
          variant="outline"
          className="h-10 w-full group-hover:bg-accent"
          tabIndex={-1}
          aria-hidden
        >
          <GoogleIcon />
          Tiếp tục với Google
        </Button>
        <div ref={container} className="absolute inset-0 overflow-hidden opacity-0" />
      </div>
    </>
  );
}
