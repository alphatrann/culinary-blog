import { describe, expect, it } from "vitest";
import { loginSchema, registerSchema } from "./schemas";

const ok = { display_name: "Minh Anh", email: "a@b.co", password: "Abcdef1!" };

describe("registerSchema", () => {
  it("accepts a valid payload", () => {
    expect(registerSchema.safeParse(ok).success).toBe(true);
  });
  it("enforces display name 2–100 chars after trim", () => {
    expect(registerSchema.safeParse({ ...ok, display_name: " a " }).success).toBe(false);
    expect(registerSchema.safeParse({ ...ok, display_name: "ab" }).success).toBe(true);
    expect(registerSchema.safeParse({ ...ok, display_name: "a".repeat(101) }).success).toBe(false);
  });
  it.each(["Abcde1!", "abcdefg1!", "Abcdefgh!", "Abcdefg12"])(
    "rejects weak password %s",
    (password) => {
      expect(registerSchema.safeParse({ ...ok, password }).success).toBe(false);
    },
  );
  it("rejects invalid email", () => {
    expect(registerSchema.safeParse({ ...ok, email: "nope" }).success).toBe(false);
  });
});

describe("loginSchema", () => {
  it("requires both fields", () => {
    expect(loginSchema.safeParse({ email: "", password: "" }).success).toBe(false);
    expect(loginSchema.safeParse({ email: "a@b.co", password: "x" }).success).toBe(true);
  });
});
