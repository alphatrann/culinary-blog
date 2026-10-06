import type { paths } from "./schema";

type Method = "get" | "post" | "put" | "patch" | "delete";

/** OpenAPI paths with the `/api/v1` base stripped, since the client prepends it. */
export type ApiPaths = {
  [K in keyof paths as K extends `/api/v1${infer P}` ? P : never]: paths[K];
};

export type PathsWith<M extends Method> = {
  [P in keyof ApiPaths]: ApiPaths[P] extends { [K in M]: unknown } ? P : never;
}[keyof ApiPaths];

type Operation<P extends keyof ApiPaths, M extends Method> = ApiPaths[P] extends {
  [K in M]: infer O;
}
  ? O
  : never;

type Params<O> = O extends { parameters: infer P } ? P : never;
type PickParam<O, K extends "path" | "query"> =
  Params<O> extends { [Key in K]?: infer V }
    ? Exclude<V, undefined> extends never
      ? never
      : Exclude<V, undefined>
    : never;

type JsonContent<R> = R extends { content: { "application/json": infer B } } ? B : never;

export type RequestBody<P extends keyof ApiPaths, M extends Method> =
  Operation<P, M> extends { requestBody?: infer B } ? JsonContent<Exclude<B, undefined>> : never;

export type ResponseBody<P extends keyof ApiPaths, M extends Method> =
  Operation<P, M> extends {
    responses: infer R;
  }
    ? R extends Record<number | string, unknown>
      ? JsonContent<R[200 | 201 | "200" | "201" extends infer K ? Extract<K, keyof R> : never]>
      : never
    : never;

type IsEmpty<T> = [T] extends [never] ? true : keyof T extends never ? true : false;

/** `path`/`query` are required only when the operation declares them. */
export type ParamOptions<P extends keyof ApiPaths, M extends Method> = (IsEmpty<
  PickParam<Operation<P, M>, "path">
> extends true
  ? { path?: never }
  : { path: PickParam<Operation<P, M>, "path"> }) &
  (IsEmpty<PickParam<Operation<P, M>, "query">> extends true
    ? { query?: never }
    : { query?: PickParam<Operation<P, M>, "query"> });
