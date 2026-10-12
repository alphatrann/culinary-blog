import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { RegisterForm } from "./register-form";

const replace = vi.fn();
const post = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace, refresh: vi.fn() }) }));
vi.mock("@/lib/api", async (orig) => ({
  ...(await orig<typeof import("@/lib/api")>()),
  api: { post: (...a: unknown[]) => post(...a) },
}));

function setup() {
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient()}>
      <RegisterForm />
    </QueryClientProvider>,
  );
  return user;
}

async function fill(user: ReturnType<typeof userEvent.setup>, password = "Abcdef1!") {
  await user.type(screen.getByLabelText("Tên hiển thị"), "Minh Anh");
  await user.type(screen.getByLabelText("Email"), "a@b.co");
  await user.type(screen.getByLabelText("Mật khẩu"), password);
  await user.click(screen.getByRole("button", { name: "Tạo tài khoản" }));
}

describe("RegisterForm", () => {
  beforeEach(() => {
    replace.mockClear();
    post.mockReset();
  });

  it("updates the password checklist live", async () => {
    const user = setup();
    const items = () => screen.getAllByRole("listitem");
    expect(items().every((li) => li.dataset.met === "false")).toBe(true);
    await user.type(screen.getByLabelText("Mật khẩu"), "Abcdef1!");
    expect(items().every((li) => li.dataset.met === "true")).toBe(true);
  });

  it("blocks a weak password", async () => {
    const user = setup();
    await fill(user, "abc");
    expect(await screen.findByText("Mật khẩu chưa đáp ứng yêu cầu.")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("registers and redirects home", async () => {
    post.mockResolvedValue({});
    const user = setup();
    await fill(user);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/"));
    expect(post).toHaveBeenCalledWith("/auth/register", {
      body: { display_name: "Minh Anh", email: "a@b.co", password: "Abcdef1!" },
    });
  });

  it("maps a duplicate email (409) onto the email field", async () => {
    post.mockRejectedValue(new ApiError(409, { detail: "dup" }));
    const user = setup();
    await fill(user);
    expect(await screen.findByText("Email này đã được đăng ký.")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "true");
  });

  it("maps server 422 field errors", async () => {
    post.mockRejectedValue(
      new ApiError(422, {
        errors: [{ loc: ["body", "display_name"], msg: "Tên không hợp lệ", type: "x" }],
      }),
    );
    const user = setup();
    await fill(user);
    expect(await screen.findByText("Tên không hợp lệ")).toBeInTheDocument();
  });
});
