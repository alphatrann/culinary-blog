import Image from "next/image";
import { Clock } from "lucide-react";
import { formatMinutes } from "@/lib/labels";

export type StepItem = {
  id: string;
  step_number: number;
  title: string;
  description: string;
  duration_minutes: number | null;
  image_url: string | null;
};

function RecipeSteps({ steps }: { steps: StepItem[] }) {
  const sorted = [...steps].sort((a, b) => a.step_number - b.step_number);
  return (
    <section aria-labelledby="steps-heading">
      <h2 id="steps-heading" className="mb-5 text-2xl font-semibold sm:text-section">
        Cách làm
      </h2>
      {sorted.length === 0 ? (
        <p className="text-muted-foreground">Công thức chưa có các bước thực hiện.</p>
      ) : (
        <ol className="m-0 flex list-none flex-col gap-7 p-0">
          {sorted.map((step) => (
            <li key={step.id} className="flex gap-4">
              <span
                aria-hidden
                className="flex size-8 shrink-0 items-center justify-center rounded-full bg-herb text-sm font-semibold text-herb-foreground"
              >
                {step.step_number}
              </span>
              <div className="min-w-0 flex-1">
                <h3 className="mt-0.5 mb-1.5 text-card-title font-semibold">
                  <span className="sr-only">Bước {step.step_number}: </span>
                  {step.title}
                </h3>
                <p className="m-0 max-w-[70ch] leading-7 whitespace-pre-line">{step.description}</p>
                {step.duration_minutes != null && (
                  <p className="mt-2 mb-0 inline-flex items-center gap-1.5 text-muted-foreground">
                    <Clock aria-hidden className="size-4" />
                    {formatMinutes(step.duration_minutes)}
                  </p>
                )}
                {step.image_url && (
                  <div className="relative mt-3 aspect-[4/3] max-w-md overflow-hidden rounded-lg border border-border bg-muted">
                    <Image
                      src={step.image_url}
                      alt={`Minh họa bước ${step.step_number}: ${step.title}`}
                      fill
                      sizes="(min-width: 768px) 448px, 100vw"
                      className="object-cover"
                    />
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

export { RecipeSteps };
