import { difficultyLabel, formatMinutes } from "@/lib/labels";

type MetaProps = {
  prepMinutes: number;
  cookMinutes: number;
  servings: number;
  difficulty: number;
};

function RecipeMeta({ prepMinutes, cookMinutes, servings, difficulty }: MetaProps) {
  const items = [
    { label: "Chuẩn bị", value: formatMinutes(prepMinutes) },
    { label: "Nấu", value: formatMinutes(cookMinutes) },
    { label: "Khẩu phần", value: `${servings} người` },
    { label: "Độ khó", value: difficultyLabel(difficulty) },
  ];
  return (
    <dl className="mt-8 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border shadow-card lg:grid-cols-4">
      {items.map((it) => (
        <div key={it.label} className="flex flex-col gap-1 bg-card p-4 sm:px-6 sm:py-5">
          <dt className="text-muted-foreground">{it.label}</dt>
          <dd className="m-0 font-heading text-xl font-semibold">{it.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export { RecipeMeta };
