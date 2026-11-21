import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { SessionUser } from "@/lib/session";
import CategoriesLayout from "./layout";

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

describe("categories layout (admin only)", () => {
  it("renders the page for an admin", () => {
    signedIn(["admin"]);
    render(<CategoriesLayout>{<p>admin content</p>}</CategoriesLayout>);

    expect(screen.getByText("admin content")).toBeInTheDocument();
  });

  it("refuses an author", () => {
    signedIn(["author"]);
    render(<CategoriesLayout>{<p>admin content</p>}</CategoriesLayout>);

    expect(screen.getByText("Bạn không có quyền truy cập trang này")).toBeInTheDocument();
    expect(screen.queryByText("admin content")).not.toBeInTheDocument();
  });
});
