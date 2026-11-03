import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi, type MockInstance } from "vitest";
import { api, ApiError } from "@/lib/api";
import { ProfileForm } from "./profile-form";

let patch: MockInstance<typeof api.patch>;

const current = {
  id: "5b1f0c7e-0000-4000-8000-000000000001",
  display_name: "Cook",
  email: "cook@example.com",
  avatar_url: null,
  bio: "Thích nấu ăn",
  roles: ["author"],
  email_confirmed: false,
  created_at: "2026-01-01T00:00:00Z",
};

vi.mock("@/lib/session", async (orig) => ({
  ...(await orig<typeof import("@/lib/session")>()),
  useUser: () => ({ user: current, status: "authenticated", logout: vi.fn() }),
}));

function setup() {
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient()}>
      <ProfileForm />
    </QueryClientProvider>,
  );
  return user;
}

describe("ProfileForm", () => {
  beforeEach(() => {
    patch = vi.spyOn(api, "patch");
  });
  afterEach(() => vi.restoreAllMocks());

  it("shows the current profile and a read-only email", () => {
    setup();
    expect(screen.getByLabelText("Tên hiển thị")).toHaveValue("Cook");
    expect(screen.getByLabelText("Giới thiệu")).toHaveValue("Thích nấu ăn");
    expect(screen.getByLabelText("Email")).toHaveAttribute("readonly");
  });

  it("keeps save disabled until something changes", async () => {
    const user = setup();
    expect(screen.getByRole("button", { name: "Lưu thay đổi" })).toBeDisabled();
    await user.type(screen.getByLabelText("Tên hiển thị"), "!");
    expect(screen.getByRole("button", { name: "Lưu thay đổi" })).toBeEnabled();
  });

  it("rejects a too-short display name without calling the API", async () => {
    const user = setup();
    const name = screen.getByLabelText("Tên hiển thị");
    await user.clear(name);
    await user.type(name, "x");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));

    expect(await screen.findByText("Tên hiển thị cần từ 2 đến 100 ký tự.")).toBeInTheDocument();
    expect(patch).not.toHaveBeenCalled();
  });

  it("sends the edited fields and null for a cleared bio", async () => {
    patch.mockResolvedValue({ ...current, display_name: "Chef" });
    const user = setup();
    const name = screen.getByLabelText("Tên hiển thị");
    await user.clear(name);
    await user.type(name, "Chef");
    await user.clear(screen.getByLabelText("Giới thiệu"));
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));

    await waitFor(() =>
      expect(patch).toHaveBeenCalledWith("/auth/me", {
        body: { display_name: "Chef", avatar_url: null, bio: null },
      }),
    );
    expect(await screen.findByRole("status")).toHaveTextContent("Đã lưu thay đổi.");
  });

  it("shows the server's field error for an invalid avatar URL", async () => {
    patch.mockRejectedValue(
      new ApiError(422, {
        title: "Validation failed",
        errors: [
          { loc: ["body", "avatar_url"], msg: "Input should be a valid URL", type: "url_parsing" },
        ],
      }),
    );
    const user = setup();
    await user.type(screen.getByLabelText("Liên kết ảnh đại diện"), "https://a.example.com/x.png");
    await user.click(screen.getByRole("button", { name: "Lưu thay đổi" }));

    expect(await screen.findByText("Input should be a valid URL")).toBeInTheDocument();
  });
});
