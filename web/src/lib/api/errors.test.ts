import { describe, expect, it } from "vitest";
import { ApiError, apiErrorFromResponse } from "./errors";

describe("ApiError code", () => {
  it("reads a known code from the problem body", () => {
    const error = new ApiError(409, { detail: "x", code: "CATEGORY_NAME_EXISTS" });
    expect(error.code).toBe("CATEGORY_NAME_EXISTS");
    expect(error.is("CATEGORY_NAME_EXISTS")).toBe(true);
    expect(error.is("CATEGORY_DELETE_HAS_RECIPES")).toBe(false);
  });

  it("treats an unknown code as absent", () => {
    expect(new ApiError(409, { code: "SOMETHING_NEW" }).code).toBeUndefined();
  });

  it("is parsed from a failed response", async () => {
    const response = new Response(
      JSON.stringify({ title: "Locked", code: "AUTH_ACCOUNT_LOCKED" }),
      {
        status: 423,
        headers: { "Content-Type": "application/problem+json" },
      },
    );
    const error = await apiErrorFromResponse(response);
    expect(error.code).toBe("AUTH_ACCOUNT_LOCKED");
    expect(error.isLocked).toBe(true);
  });

  it("prefers the code over the status for conflicts", () => {
    // A 409 that is not a concurrency conflict (e.g. duplicate category name) must not open the reload dialog.
    expect(new ApiError(409, { code: "CATEGORY_NAME_EXISTS" }).isConflict).toBe(false);
    expect(new ApiError(409, { code: "RECIPE_CONCURRENCY_CONFLICT" }).isConflict).toBe(true);
  });

  it("falls back to the status when no code is sent", () => {
    expect(new ApiError(409, {}).isConflict).toBe(true);
    expect(new ApiError(423, {}).isLocked).toBe(true);
    expect(new ApiError(429, {}).isRateLimited).toBe(true);
  });
});
