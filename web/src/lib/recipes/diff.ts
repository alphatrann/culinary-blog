/**
 * Turns the form's child rows (ingredients or steps) into the API calls that bring the server in line with them.
 * Pure: no I/O, so the rules can be tested without the network.
 */

/** What the server currently holds for one child, as the form would send it. */
export interface Snapshot<P> {
  id: string;
  payload: P;
}

/** One form row. `payload` is `null` for a blank row, which is dropped. `rowIndex` is its position in the form array. */
export interface Row<P> {
  rowIndex: number;
  id?: string;
  payload: P | null;
}

export type Op<P> =
  | { kind: "delete"; id: string }
  | { kind: "create"; rowIndex: number; payload: P }
  | { kind: "update"; rowIndex: number; id: string; payload: P };

/**
 * `ordered` lists (steps) have no position field on the API, so the server's order is the order of creation.
 * If the form reorders them, or puts a new row before an existing one, every child is recreated in form order.
 */
export function planChildOps<P>(
  snapshot: Snapshot<P>[],
  rows: Row<P>[],
  { ordered }: { ordered: boolean },
): Op<P>[] {
  const kept = rows.filter((r): r is Row<P> & { payload: P } => r.payload !== null);
  const serverIds = new Set(snapshot.map((s) => s.id));
  const isExisting = (r: Row<P>) => r.id !== undefined && serverIds.has(r.id);
  const keptExisting = kept.filter(isExisting).map((r) => r.id!);
  const keptExistingSet = new Set(keptExisting);

  if (ordered) {
    const firstNew = kept.findIndex((r) => !isExisting(r));
    const newBeforeExisting = firstNew !== -1 && kept.slice(firstNew).some(isExisting);
    const serverOrder = snapshot.map((s) => s.id).filter((id) => keptExistingSet.has(id));
    const reordered = keptExisting.join() !== serverOrder.join();
    if (newBeforeExisting || reordered) {
      return [
        ...snapshot.map((s): Op<P> => ({ kind: "delete", id: s.id })),
        ...kept.map((r): Op<P> => ({ kind: "create", rowIndex: r.rowIndex, payload: r.payload })),
      ];
    }
  }

  const deletes = snapshot
    .filter((s) => !keptExistingSet.has(s.id))
    .map((s): Op<P> => ({ kind: "delete", id: s.id }));

  const writes = kept.flatMap((r): Op<P>[] => {
    const existing = isExisting(r) ? snapshot.find((s) => s.id === r.id) : undefined;
    if (!existing) return [{ kind: "create", rowIndex: r.rowIndex, payload: r.payload }];
    if (JSON.stringify(existing.payload) === JSON.stringify(r.payload)) return [];
    return [{ kind: "update", rowIndex: r.rowIndex, id: r.id!, payload: r.payload }];
  });

  return [...deletes, ...writes];
}
