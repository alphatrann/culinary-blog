import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const initialize = vi.fn();
const renderButton = vi.fn();

beforeEach(() => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.resetModules();
  delete window.google;
});

describe("GoogleSignInButton", () => {
  it("renders nothing when NEXT_PUBLIC_GOOGLE_CLIENT_ID is unset", async () => {
    const { GoogleSignInButton } = await import("./google-sign-in-button");
    const { container } = render(<GoogleSignInButton onCredential={vi.fn()} />);

    expect(container).toBeEmptyDOMElement();
  });

  describe("when configured", () => {
    beforeEach(() => {
      vi.stubEnv("NEXT_PUBLIC_GOOGLE_CLIENT_ID", "test-client-id");
      window.google = { accounts: { id: { initialize, renderButton } } };
    });

    it("initializes Identity Services and passes the ID token to onCredential", async () => {
      const { GoogleSignInButton } = await import("./google-sign-in-button");
      const onCredential = vi.fn();
      render(<GoogleSignInButton onCredential={onCredential} />);

      expect(initialize).toHaveBeenCalledWith(
        expect.objectContaining({ client_id: "test-client-id" }),
      );
      expect(renderButton).toHaveBeenCalledWith(
        expect.any(HTMLElement),
        expect.objectContaining({ size: "large" }),
      );
      expect(screen.getByText("Hoặc")).toBeInTheDocument();

      initialize.mock.calls[0][0].callback({ credential: "signed.id.token" });
      expect(onCredential).toHaveBeenCalledWith("signed.id.token");
    });
  });
});
