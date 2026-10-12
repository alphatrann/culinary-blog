import { describe, expect, it } from "vitest";
import { ApiError } from "@/lib/api";
import { mapAuthError } from "./errors";

const err = (status: number, extra = {}) => new ApiError(status, { detail: "x", ...extra });

describe("mapAuthError", () => {
  it("maps 401 to the generic credentials message", () => {
    expect(mapAuthError(err(401), "login").banner).toBe("Email hoặc mật khẩu không đúng.");
  });
  it("maps 423 lockout and 429", () => {
    expect(mapAuthError(err(423), "login").banner).toMatch(/15 phút/);
    expect(mapAuthError(err(429), "login").banner).toMatch(/quá nhanh/);
  });
  it("maps register 409 onto the email field", () => {
    const r = mapAuthError(err(409), "register");
    expect(r.fields.email).toBeTruthy();
    expect(r.banner).toMatch(/đã được đăng ký/);
  });
  it("maps 422 field errors", () => {
    const r = mapAuthError(
      err(422, { errors: [{ loc: ["body", "password"], msg: "bad", type: "value_error" }] }),
      "register",
    );
    expect(r.fields).toEqual({ password: "bad" });
  });
  it("falls back for unknown errors", () => {
    expect(mapAuthError(new Error("boom"), "login").banner).toBeTruthy();
  });
});
