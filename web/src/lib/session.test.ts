import { describe, expect, it } from "vitest";
import { hasRole, initials, type SessionUser } from "./session";

const user = (roles: string[]): SessionUser => ({
  id: "1",
  display_name: "A",
  email: "a@b.c",
  avatar_url: null,
  bio: null,
  roles,
  email_confirmed: false,
  created_at: "2026-01-01T00:00:00Z",
});

describe("hasRole", () => {
  it("is false for guests", () => expect(hasRole(null, "author")).toBe(false));
  it("matches any listed role", () =>
    expect(hasRole(user(["author"]), "admin", "author")).toBe(true));
  it("lets admin satisfy any role", () => expect(hasRole(user(["admin"]), "author")).toBe(true));
  it("rejects missing role", () => expect(hasRole(user(["reader"]), "author")).toBe(false));
});

describe("initials", () => {
  it("uses first and last word", () => expect(initials("Trần Thái Anh")).toBe("TA"));
  it("handles single and empty names", () => {
    expect(initials("an")).toBe("A");
    expect(initials("  ")).toBe("?");
  });
});
