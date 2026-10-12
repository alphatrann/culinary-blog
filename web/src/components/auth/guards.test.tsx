import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, ApiError } from "@/lib/api";
import { GuestOnly } from "./guest-only";
import { RequireAuth } from "./require-auth";

const replace = vi.fn();
let pathname = "/dashboard";
let search = "tab=a";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => pathname,
  useSearchParams: () => new URLSearchParams(search),
}));

function renderWithClient(ui: ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

const me = (roles: string[]) =>
  vi.spyOn(api, "get").mockResolvedValue({
    id: "1",
    display_name: "An",
    email: "a@b.c",
    avatar_url: null,
    roles,
  } as never);
const guest = () =>
  vi.spyOn(api, "get").mockRejectedValue(new ApiError(401, { title: "Unauthorized" }));

beforeEach(() => {
  vi.restoreAllMocks();
  replace.mockClear();
  pathname = "/dashboard";
  search = "tab=a";
});

describe("RequireAuth", () => {
  it("hides content while loading", () => {
    vi.spyOn(api, "get").mockReturnValue(new Promise(() => {}) as never);
    renderWithClient(<RequireAuth>secret</RequireAuth>);
    expect(screen.queryByText("secret")).toBeNull();
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects guests to login with next", async () => {
    guest();
    renderWithClient(<RequireAuth>secret</RequireAuth>);
    await waitFor(() =>
      expect(replace).toHaveBeenCalledWith("/auth/login?next=%2Fdashboard%3Ftab%3Da"),
    );
    expect(screen.queryByText("secret")).toBeNull();
  });

  it("renders children for a user with the role", async () => {
    me(["author"]);
    renderWithClient(<RequireAuth roles={["author", "admin"]}>secret</RequireAuth>);
    expect(await screen.findByText("secret")).toBeInTheDocument();
  });

  it("shows a 403 state when the role is missing", async () => {
    me(["reader"]);
    renderWithClient(<RequireAuth roles={["author"]}>secret</RequireAuth>);
    expect(await screen.findByText(/không có quyền/i)).toBeInTheDocument();
    expect(screen.queryByText("secret")).toBeNull();
    expect(replace).not.toHaveBeenCalled();
  });
});

describe("GuestOnly", () => {
  it("renders children for guests", async () => {
    guest();
    renderWithClient(<GuestOnly>form</GuestOnly>);
    expect(await screen.findByText("form")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("shows a loading state instead of the form for signed-in users", async () => {
    me(["author"]);
    renderWithClient(<GuestOnly>form</GuestOnly>);
    expect(await screen.findByText("Đang chuyển hướng…")).toBeInTheDocument();
    expect(screen.queryByText("form")).toBeNull();
  });

  it("sends signed-in users to a safe next, else home", async () => {
    me(["author"]);
    search = "next=%2Fprofile";
    const { unmount } = renderWithClient(<GuestOnly>form</GuestOnly>);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/profile"));
    unmount();

    replace.mockClear();
    search = "next=%2F%2Fevil.com";
    renderWithClient(<GuestOnly>form</GuestOnly>);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/"));
  });
});
