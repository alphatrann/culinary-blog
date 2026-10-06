import { describe, expect, it, vi } from "vitest";
import { ApiClient } from "./client";
import { ApiError } from "./errors";

const json = (body: unknown, status = 200, type = "application/json") =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": type } });

const user = { id: "1" };

function setup(handler: (url: string, init: RequestInit) => Response | Promise<Response>) {
  const fetchImpl = vi.fn((url: string | URL | Request, init?: RequestInit) =>
    Promise.resolve(handler(String(url), init ?? {})),
  );
  return { fetchImpl, client: new ApiClient("/api/v1", fetchImpl as unknown as typeof fetch) };
}

describe("ApiClient", () => {
  it("sends credentials, correlation id, If-Match and JSON body", async () => {
    const { client, fetchImpl } = setup(() => json({}));
    await client.put(
      "/recipes/{recipe_id}" as never,
      {
        path: { recipe_id: "a b" },
        body: { title: "x" },
        rowVersion: 3,
        correlationId: "cid",
      } as never,
    );
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Headers;
    expect(url).toBe("/api/v1/recipes/a%20b");
    expect(init.credentials).toBe("include");
    expect(headers.get("If-Match")).toBe("3");
    expect(headers.get("X-Correlation-ID")).toBe("cid");
    expect(headers.get("Content-Type")).toBe("application/json");
    expect(headers.has("Authorization")).toBe(false);
  });

  it("does not set Content-Type for multipart bodies", async () => {
    const { client, fetchImpl } = setup(() => json({}));
    await client.post(
      "/recipes/{recipe_id}/images" as never,
      { path: { recipe_id: "1" }, formData: new FormData() } as never,
    );
    expect(
      ((fetchImpl.mock.calls[0]![1] as RequestInit).headers as Headers).has("Content-Type"),
    ).toBe(false);
  });

  it("parses problem+json into ApiError with field errors", async () => {
    const { client } = setup(() =>
      json(
        {
          title: "Unprocessable Entity",
          detail: "Request validation failed",
          errors: [{ loc: ["body", "title"], msg: "too short", type: "x" }],
        },
        422,
        "application/problem+json",
      ),
    );
    const error = await client.get("/auth/me").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(422);
    expect((error as ApiError).errors).toEqual({ title: "too short" });
  });

  it("refreshes once (single-flight) and retries concurrent 401s", async () => {
    let refreshed = false;
    const { client, fetchImpl } = setup((url) => {
      if (url.endsWith("/auth/refresh")) {
        refreshed = true;
        return json(user);
      }
      return refreshed
        ? json(user)
        : json({ title: "Unauthorized" }, 401, "application/problem+json");
    });
    const results = await Promise.all([
      client.get("/auth/me"),
      client.get("/auth/me"),
      client.get("/auth/me"),
    ]);
    expect(results).toEqual([user, user, user]);
    expect(fetchImpl.mock.calls.filter(([u]) => String(u).endsWith("/auth/refresh"))).toHaveLength(
      1,
    );
  });

  it("surfaces signed-out state when refresh fails", async () => {
    const { client } = setup(() =>
      json({ title: "Unauthorized" }, 401, "application/problem+json"),
    );
    const onSignedOut = vi.fn();
    client.onSignedOut(onSignedOut);
    await expect(client.get("/auth/me")).rejects.toMatchObject({ status: 401 });
    expect(onSignedOut).toHaveBeenCalledOnce();
  });

  it("does not refresh on login 401", async () => {
    const { client, fetchImpl } = setup(() =>
      json({ title: "Unauthorized" }, 401, "application/problem+json"),
    );
    await expect(
      client.post("/auth/login", { body: { email: "a@b.c", password: "x" } }),
    ).rejects.toBeInstanceOf(ApiError);
    expect(fetchImpl).toHaveBeenCalledOnce();
  });

  it("returns undefined for 204", async () => {
    const { client } = setup(() => new Response(null, { status: 204 }));
    await expect(client.post("/auth/logout")).resolves.toBeUndefined();
  });
});
