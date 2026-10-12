import { describe, expect, it } from "vitest";
import { loginUrl, safeNext } from "./next-url";

describe("safeNext", () => {
  it("accepts same-origin paths", () => {
    expect(safeNext("/dashboard?x=1")).toBe("/dashboard?x=1");
  });

  it.each([null, "", "dashboard", "//evil.com", "https://evil.com", "/\\evil.com", "/a\nb"])(
    "rejects %j",
    (raw) => {
      expect(safeNext(raw)).toBeNull();
    },
  );
});

describe("loginUrl", () => {
  it("encodes the destination", () => {
    expect(loginUrl("/dashboard?tab=a")).toBe("/auth/login?next=%2Fdashboard%3Ftab%3Da");
  });

  it("omits next for home or unsafe values", () => {
    expect(loginUrl("/")).toBe("/auth/login");
    expect(loginUrl("//evil.com")).toBe("/auth/login");
  });
});
