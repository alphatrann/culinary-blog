import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { SessionUser } from "@/lib/session";
import CategoriesPage from "./page";

const useUser = vi.fn();
vi.mock("@/lib/session", async (orig) => ({
  ...(await orig<typeof import("@/lib/session")>()),
  useUser: () => useUser(),
}));
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn() }),
  usePathname: () => "/dashboard/categories",
  useSearchParams: () => new URLSearchParams(),
}));

const signedIn = (roles: string[]) =>
  useUser.mockReturnValue({
    status: "authenticated",
    user: { display_name: "Test", roles } as unknown as SessionUser,
  });

describe("categories page (admin only)", () => {
  it("shows the placeholder to an admin", () => {
    signedIn(["admin"]);
    render(<CategoriesPage />);

    expect(screen.getByText("Sắp ra mắt")).toBeInTheDocument();
  });

  it("refuses an author", () => {
    signedIn(["author"]);
    render(<CategoriesPage />);

    expect(screen.getByText("Bạn không có quyền truy cập trang này")).toBeInTheDocument();
    expect(screen.queryByText("Sắp ra mắt")).not.toBeInTheDocument();
  });
});
