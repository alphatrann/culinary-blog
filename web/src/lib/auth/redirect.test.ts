import { describe, expect, it } from "vitest";
import { safeNext, withNext } from "./redirect";

describe("safeNext", () => {
  it("allows same-origin paths", () => {
    expect(safeNext("/recipes?page=2")).toBe("/recipes?page=2");
  });
  it.each(["//evil.com", "https://evil.com", "/\\evil.com", "recipes", "/a\nb", undefined, ["/a"]])(
    "rejects %s",
    (v) => expect(safeNext(v as string)).toBeNull(),
  );
});

describe("withNext", () => {
  it("appends an encoded next param", () => {
    expect(withNext("/auth/login", "/a?b=1")).toBe("/auth/login?next=%2Fa%3Fb%3D1");
    expect(withNext("/auth/login", null)).toBe("/auth/login");
  });
});
