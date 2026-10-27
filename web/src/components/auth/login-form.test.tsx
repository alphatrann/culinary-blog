import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { LoginForm } from "./login-form";

const replace = vi.fn();
const post = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace, refresh: vi.fn() }) }));
vi.mock("@/components/auth/google-sign-in-button", () => ({
  GoogleSignInButton: ({ onCredential }: { onCredential: (token: string) => void }) => (
    <button type="button" onClick={() => onCredential("google.id.token")}>
      Google stub
    </button>
  ),
}));
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: { post: (...a: unknown[]) => post(...a) },
}));

function setup(next?: string | null) {
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient()}>
      <LoginForm next={next} />
    </QueryClientProvider>,
  );
  return user;
}

async function fill(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText("Email"), "a@b.co");
  await user.type(screen.getByLabelText("Mật khẩu"), "secret");
  await user.click(screen.getByRole("button", { name: "Đăng nhập" }));
}

describe("LoginForm", () => {
  beforeEach(() => {
    replace.mockClear();
    post.mockReset();
  });

  it("shows validation errors and does not submit", async () => {
    const user = setup();
    await user.click(screen.getByRole("button", { name: "Đăng nhập" }));
    expect(await screen.findByText("Vui lòng nhập email.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("toggles password visibility", async () => {
    const user = setup();
    const input = screen.getByLabelText("Mật khẩu");
    expect(input).toHaveAttribute("type", "password");
    await user.click(screen.getByRole("button", { name: "Hiện mật khẩu" }));
    expect(input).toHaveAttribute("type", "text");
  });

  it("redirects to a safe next on success", async () => {
    post.mockResolvedValue({});
    const user = setup("/recipes");
    await fill(user);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/recipes"));
    expect(post).toHaveBeenCalledWith("/auth/login", {
      body: { email: "a@b.co", password: "secret" },
    });
  });

  it("falls back to / for an unsafe next", async () => {
    post.mockResolvedValue({});
    const user = setup("//evil.com");
    await fill(user);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/"));
  });

  it.each([
    [401, /Email hoặc mật khẩu không đúng/],
    [423, /tạm khóa/],
    [429, /quá nhanh/],
  ])("shows a banner for %s", async (status, message) => {
    post.mockRejectedValue(new ApiError(status, { detail: "x" }));
    const user = setup();
    await fill(user);
    expect(await screen.findByRole("alert")).toHaveTextContent(message);
    expect(replace).not.toHaveBeenCalled();
  });

  it("posts the Google ID token to /auth/google and redirects on success", async () => {
    post.mockResolvedValue({});
    const user = setup("/recipes");
    await user.click(screen.getByRole("button", { name: "Google stub" }));

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/recipes"));
    expect(post).toHaveBeenCalledWith("/auth/google", { body: { id_token: "google.id.token" } });
  });

  it("shows the generic banner when the Google token is rejected", async () => {
    post.mockRejectedValue(
      new ApiError(401, { title: "Unauthorized", detail: "Invalid Google ID token" }),
    );
    const user = setup();
    await user.click(screen.getByRole("button", { name: "Google stub" }));

    expect(await screen.findByText("Email hoặc mật khẩu không đúng.")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });
});
