import { describe, expect, it } from "vitest";
import { planChildOps, type Row, type Snapshot } from "./diff";

type P = { text: string };
const snap = (id: string, text: string): Snapshot<P> => ({ id, payload: { text } });
const row = (rowIndex: number, text: string | null, id?: string): Row<P> => ({
  rowIndex,
  id,
  payload: text === null ? null : { text },
});

describe("planChildOps", () => {
  it("emits nothing when the form matches the server", () => {
    const server = [snap("a", "one"), snap("b", "two")];
    const form = [row(0, "one", "a"), row(1, "two", "b")];

    expect(planChildOps(server, form, { ordered: false })).toEqual([]);
    expect(planChildOps(server, form, { ordered: true })).toEqual([]);
  });

  it("updates only rows whose payload changed", () => {
    const server = [snap("a", "one"), snap("b", "two")];

    expect(
      planChildOps(server, [row(0, "one", "a"), row(1, "TWO", "b")], { ordered: false }),
    ).toEqual([{ kind: "update", rowIndex: 1, id: "b", payload: { text: "TWO" } }]);
  });

  it("creates rows without an id and deletes server rows that were removed", () => {
    const server = [snap("a", "one"), snap("b", "two")];

    expect(planChildOps(server, [row(0, "one", "a"), row(1, "new")], { ordered: false })).toEqual([
      { kind: "delete", id: "b" },
      { kind: "create", rowIndex: 1, payload: { text: "new" } },
    ]);
  });

  it("drops blank rows and treats them as absent", () => {
    const server = [snap("a", "one")];

    expect(planChildOps(server, [row(0, "one", "a"), row(1, null)], { ordered: false })).toEqual(
      [],
    );
  });

  it("creates a row whose id the server no longer has", () => {
    // e.g. another tab deleted it after this form loaded
    const server = [snap("a", "one")];

    expect(planChildOps(server, [row(0, "gone", "x")], { ordered: false })).toEqual([
      { kind: "delete", id: "a" },
      { kind: "create", rowIndex: 0, payload: { text: "gone" } },
    ]);
  });

  it("appends new steps without recreating when existing order is kept", () => {
    const server = [snap("a", "one"), snap("b", "two")];

    expect(
      planChildOps(server, [row(0, "one", "a"), row(1, "two", "b"), row(2, "three")], {
        ordered: true,
      }),
    ).toEqual([{ kind: "create", rowIndex: 2, payload: { text: "three" } }]);
  });

  it("recreates every step when the form reorders them", () => {
    const server = [snap("a", "one"), snap("b", "two")];

    expect(
      planChildOps(server, [row(0, "two", "b"), row(1, "one", "a")], { ordered: true }),
    ).toEqual([
      { kind: "delete", id: "a" },
      { kind: "delete", id: "b" },
      { kind: "create", rowIndex: 0, payload: { text: "two" } },
      { kind: "create", rowIndex: 1, payload: { text: "one" } },
    ]);
  });

  it("recreates every step when a new step is inserted before an existing one", () => {
    const server = [snap("a", "one"), snap("b", "two")];

    const ops = planChildOps(server, [row(0, "zero"), row(1, "one", "a"), row(2, "two", "b")], {
      ordered: true,
    });

    expect(ops.filter((o) => o.kind === "delete")).toHaveLength(2);
    expect(ops.filter((o) => o.kind === "create").map((o) => o.rowIndex)).toEqual([0, 1, 2]);
  });

  it("does not recreate unordered children when they are reordered", () => {
    // Ingredients are not recreated on reorder; their order_index is part of the payload, so a reorder that
    // changes it shows up as an update (covered by the payload-equality test above).
    const server = [snap("a", "one"), snap("b", "two")];

    expect(
      planChildOps(server, [row(0, "two", "b"), row(1, "one", "a")], { ordered: false }),
    ).toEqual([]);
  });
});
