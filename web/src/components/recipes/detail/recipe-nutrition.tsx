export type Nutrition = {
  calories?: number | null;
  protein?: number | null;
  carbohydrates?: number | null;
  fat?: number | null;
  fiber?: number | null;
  sodium?: number | null;
};

const fields: { key: keyof Nutrition; label: string; unit: string }[] = [
  { key: "calories", label: "Năng lượng", unit: "kcal" },
  { key: "protein", label: "Chất đạm", unit: "g" },
  { key: "fat", label: "Chất béo", unit: "g" },
  { key: "carbohydrates", label: "Carbohydrate", unit: "g" },
  { key: "fiber", label: "Chất xơ", unit: "g" },
  { key: "sodium", label: "Natri", unit: "mg" },
];

const numberFormat = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 1 });

/** Renders nothing when the recipe has no nutrition data. */
function RecipeNutrition({ nutrition }: { nutrition: Nutrition }) {
  const present = fields.filter((f) => nutrition[f.key] != null);
  if (present.length === 0) return null;
  return (
    <section aria-labelledby="nutrition-heading" className="mt-14">
      <h2 id="nutrition-heading" className="mb-5 text-2xl font-semibold sm:text-section">
        Giá trị dinh dưỡng mỗi khẩu phần
      </h2>
      <dl className="m-0 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {present.map((f) => (
          <div
            key={f.key}
            className="rounded-xl border border-border bg-card px-5 py-4 shadow-card"
          >
            <dt className="text-muted-foreground">{f.label}</dt>
            <dd className="m-0 mt-1 text-2xl font-semibold tabular-nums">
              {numberFormat.format(nutrition[f.key] as number)} {f.unit}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

export { RecipeNutrition };
