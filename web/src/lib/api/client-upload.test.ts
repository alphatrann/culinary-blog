import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiClient } from "./client";

/** Minimal XMLHttpRequest double: `respond` decides each reply, and `upload.onprogress` is driven by the test. */
class FakeXHR {
  static instances: FakeXHR[] = [];
  static respond: (xhr: FakeXHR, attempt: number) => void = () => undefined;

  upload: { onprogress: ((e: ProgressEvent) => void) | null } = { onprogress: null };
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onabort: (() => void) | null = null;
  status = 0;
  responseText = "";
  withCredentials = false;
  method = "";
  url = "";
  sent: unknown;
  readonly headers = new Map<string, string>();

  constructor() {
    FakeXHR.instances.push(this);
  }

  open(method: string, url: string) {
    this.method = method;
    this.url = url;
  }

  setRequestHeader(key: string, value: string) {
    this.headers.set(key, value);
  }

  getResponseHeader(key: string) {
    return key === "Content-Type" ? "application/json" : null;
  }

  send(body: unknown) {
    this.sent = body;
    const attempt = FakeXHR.instances.length;
    queueMicrotask(() => FakeXHR.respond(this, attempt));
  }

  abort() {
    this.onabort?.();
  }
}

const reply = (xhr: FakeXHR, status: number, body: unknown) => {
  xhr.status = status;
  xhr.responseText = JSON.stringify(body);
  xhr.onload?.();
};

afterEach(() => {
  vi.unstubAllGlobals();
  FakeXHR.instances = [];
});

describe("ApiClient upload with progress", () => {
  it("reports fractional progress and resolves with the parsed body", async () => {
    vi.stubGlobal("XMLHttpRequest", FakeXHR);
    const created = { id: "img-1", is_primary: true };
    FakeXHR.respond = (xhr) => reply(xhr, 201, created);
    const onProgress = vi.fn();
    const fetchImpl = vi.fn();
    const client = new ApiClient("/api/v1", fetchImpl as unknown as typeof fetch);
    const formData = new FormData();

    const pending = client.post(
      "/recipes/{recipe_id}/images" as never,
      {
        path: { recipe_id: "r1" },
        formData,
        onProgress,
      } as never,
    );
    await vi.waitFor(() => expect(FakeXHR.instances).toHaveLength(1));
    const xhr = FakeXHR.instances[0]!;
    xhr.upload.onprogress?.({ lengthComputable: true, loaded: 50, total: 100 } as ProgressEvent);

    await expect(pending).resolves.toEqual(created);
    expect(onProgress).toHaveBeenCalledWith(0.5);
    expect(xhr.url).toBe("/api/v1/recipes/r1/images");
    expect(xhr.method).toBe("POST");
    expect(xhr.withCredentials).toBe(true);
    expect(xhr.sent).toBe(formData);
    // Headers are normalised to lowercase names by the Headers object.
    expect(xhr.headers.has("content-type")).toBe(false);
    expect(xhr.headers.get("x-correlation-id")).toBeTruthy();
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("refreshes once on 401 and retries the upload", async () => {
    vi.stubGlobal("XMLHttpRequest", FakeXHR);
    FakeXHR.respond = (xhr, attempt) =>
      attempt === 1 ? reply(xhr, 401, { title: "Unauthorized" }) : reply(xhr, 201, { id: "img-2" });
    const fetchImpl = vi.fn<(url: string) => Promise<Response>>(() =>
      Promise.resolve(new Response("{}", { status: 200 })),
    );
    const client = new ApiClient("/api/v1", fetchImpl as unknown as typeof fetch);

    const result = await client.post(
      "/recipes/{recipe_id}/images" as never,
      {
        path: { recipe_id: "r1" },
        formData: new FormData(),
        onProgress: () => undefined,
      } as never,
    );

    expect(result).toEqual({ id: "img-2" });
    expect(FakeXHR.instances).toHaveLength(2);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    expect(String(fetchImpl.mock.calls[0]![0])).toBe("/api/v1/auth/refresh");
  });

  it("throws ApiError for a non-2xx upload response", async () => {
    vi.stubGlobal("XMLHttpRequest", FakeXHR);
    FakeXHR.respond = (xhr) =>
      reply(xhr, 400, { title: "Bad Request", detail: "Ảnh vượt quá dung lượng tối đa 5 MB." });
    const client = new ApiClient("/api/v1", vi.fn() as unknown as typeof fetch);

    await expect(
      client.post(
        "/recipes/{recipe_id}/images" as never,
        {
          path: { recipe_id: "r1" },
          formData: new FormData(),
          onProgress: () => undefined,
        } as never,
      ),
    ).rejects.toMatchObject({ status: 400, detail: "Ảnh vượt quá dung lượng tối đa 5 MB." });
  });

  it("rejects with AbortError when the signal aborts", async () => {
    vi.stubGlobal("XMLHttpRequest", FakeXHR);
    FakeXHR.respond = () => undefined;
    const client = new ApiClient("/api/v1", vi.fn() as unknown as typeof fetch);
    const controller = new AbortController();

    const pending = client.post(
      "/recipes/{recipe_id}/images" as never,
      {
        path: { recipe_id: "r1" },
        formData: new FormData(),
        onProgress: () => undefined,
        signal: controller.signal,
      } as never,
    );
    await vi.waitFor(() => expect(FakeXHR.instances).toHaveLength(1));
    controller.abort();

    await expect(pending).rejects.toMatchObject({ name: "AbortError" });
  });
});
