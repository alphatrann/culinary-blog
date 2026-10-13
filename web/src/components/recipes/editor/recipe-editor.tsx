"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { FormProvider, useForm, useWatch } from "react-hook-form";
import { Alert } from "@/components/ui/alert";
import { api, type ResponseBody } from "@/lib/api";
import { mapRecipeError } from "@/lib/recipes/errors";
import {
  emptyRecipeForm,
  isPublishable,
  recipeFormSchema,
  toCreatePayload,
  type RecipeFormValues,
} from "@/lib/recipes/schemas";
import { useUnsavedChanges } from "@/lib/use-unsaved-changes";
import { BasicInfoCard } from "./basic-info-card";
import { IngredientsCard } from "./ingredients-card";
import { NutritionCard } from "./nutrition-card";
import { PublishCard } from "./publish-card";
import { StepsCard } from "./steps-card";

type Recipe = ResponseBody<"/recipes", "post">;
type Mode = "draft" | "publish";

export function RecipeEditor() {
  const router = useRouter();
  const [banner, setBanner] = useState<string>();
  const [done, setDone] = useState(false);
  // A draft that was created but failed to publish; retries only call publish.
  const created = useRef<Recipe | null>(null);

  const form = useForm<RecipeFormValues>({
    resolver: zodResolver(recipeFormSchema),
    defaultValues: emptyRecipeForm,
  });
  const { handleSubmit, setError, control, formState } = form;

  const ingredients = useWatch({ control, name: "ingredients" });
  const steps = useWatch({ control, name: "steps" });
  const checklist = isPublishable({ ingredients: ingredients ?? [], steps: steps ?? [] });

  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/categories"),
    staleTime: 5 * 60_000,
  });

  const save = useMutation({
    mutationFn: async ({ values, mode }: { values: RecipeFormValues; mode: Mode }) => {
      if (!created.current) {
        created.current = await api.post("/recipes", { body: toCreatePayload(values) });
      }
      const draft = created.current;
      if (mode === "publish") {
        return await api.patch("/recipes/{recipe_id}/publish", { path: { recipe_id: draft.id } });
      }
      return draft;
    },
    onSuccess: (recipe, { mode }) => {
      setDone(true);
      router.push(mode === "publish" ? `/recipes/${recipe.slug}` : "/dashboard/recipes");
    },
    onError: (error) => {
      const failure = mapRecipeError(error);
      const draftSaved = created.current !== null;
      setBanner(
        draftSaved
          ? `Đã lưu bản nháp nhưng chưa xuất bản được. ${failure.banner ?? ""}`.trim()
          : failure.banner,
      );
      for (const [field, message] of Object.entries(failure.fields)) {
        setError(field as keyof RecipeFormValues, { message });
      }
    },
  });

  useUnsavedChanges(formState.isDirty && !done);

  const submit = (mode: Mode) =>
    handleSubmit((values) => {
      setBanner(undefined);
      save.mutate({ values, mode });
    })();

  const pending: Mode | null = save.isPending ? (save.variables?.mode ?? null) : null;

  return (
    <FormProvider {...form}>
      <form noValidate onSubmit={(e) => e.preventDefault()} className="flex flex-col gap-6">
        {banner && <Alert>{banner}</Alert>}
        <div className="grid items-start gap-6 min-[1000px]:grid-cols-[1fr_360px]">
          <div className="flex flex-col gap-6 min-[1000px]:order-2">
            <PublishCard
              hasIngredients={checklist.ingredients}
              hasSteps={checklist.steps}
              pending={pending}
              onSaveDraft={() => submit("draft")}
              onPublish={() => submit("publish")}
            />
            <NutritionCard />
          </div>
          <div className="flex flex-col gap-6 min-[1000px]:order-1">
            <BasicInfoCard
              categories={categories.data ?? []}
              categoriesLoading={categories.isPending}
            />
            <IngredientsCard />
            <StepsCard />
          </div>
        </div>
      </form>
    </FormProvider>
  );
}
